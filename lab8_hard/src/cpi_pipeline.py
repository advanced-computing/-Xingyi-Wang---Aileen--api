from __future__ import annotations

import argparse
import re
import time
from functools import lru_cache
from pathlib import Path

import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "pcpiMvMd.xlsx"
DB_PATH = BASE_DIR / "cpi.duckdb"
SCRIPTS_DIR = BASE_DIR / "scripts"


@lru_cache(maxsize=1)
def load_source_data() -> pd.DataFrame:
    """
    Load the raw Excel file once and cache it.
    """
    df = pd.read_excel(DATA_PATH, na_values=["#N/A"])
    return df


def parse_vintage(col_name: str) -> pd.Timestamp | None:
    """
    Parse column names like PCPI04M1, PCPI04M2, ..., PCPI25M12
    into a pandas Timestamp representing the vintage month.
    """
    match = re.fullmatch(r"PCPI(\d{2})M(\d{1,2})", col_name)
    if not match:
        return None

    yy = int(match.group(1))
    month = int(match.group(2))
    year = 2000 + yy
    return pd.Timestamp(year=year, month=month, day=1)


def parse_obs_date(series: pd.Series) -> pd.Series:
    """
    Convert DATE values like '2003:09' into pandas datetime.
    """
    return pd.to_datetime(series.astype(str), format="%Y:%m")


def get_latest_data(pull_date: str | pd.Timestamp) -> pd.DataFrame:
    """
    Return the latest CPI data available up to pull_date.

    Output columns:
      - obs_date
      - cpi
    """
    pull_date = pd.Timestamp(pull_date)
    raw = load_source_data().copy()

    vintage_cols = []
    for col in raw.columns:
        vintage_date = parse_vintage(str(col))
        if vintage_date is not None and vintage_date <= pull_date:
            vintage_cols.append((col, vintage_date))

    if not vintage_cols:
        return pd.DataFrame(columns=["obs_date", "cpi"])

    latest_col = max(vintage_cols, key=lambda x: x[1])[0]

    out = raw.loc[:, ["DATE", latest_col]].copy()
    out["DATE"] = parse_obs_date(out["DATE"])
    out = out.rename(columns={"DATE": "obs_date", latest_col: "cpi"})
    out = out.dropna(subset=["cpi"]).sort_values("obs_date").reset_index(drop=True)

    return out[["obs_date", "cpi"]]


def run_sql_script(con: duckdb.DuckDBPyConnection, script_name: str) -> None:
    script_path = SCRIPTS_DIR / script_name
    sql = script_path.read_text(encoding="utf-8")
    con.execute(sql)


def init_db(db_path: Path = DB_PATH) -> None:
    con = duckdb.connect(str(db_path))
    try:
        run_sql_script(con, "init_db.sql")
    finally:
        con.close()


def load_method(method: str, pull_date: str, db_path: Path = DB_PATH) -> None:
    if method not in {"append", "trunc", "inc"}:
        raise ValueError("method must be one of: append, trunc, inc")

    latest_data = get_latest_data(pull_date)
    pull_date_ts = pd.Timestamp(pull_date).normalize()

    con = duckdb.connect(str(db_path))
    try:
        run_sql_script(con, "init_db.sql")

        run_context = pd.DataFrame({"pull_date": [pull_date_ts]})

        con.register("latest_data", latest_data)
        con.register("run_context", run_context)

        run_sql_script(con, f"load_{method}.sql")

        con.unregister("latest_data")
        con.unregister("run_context")
    finally:
        con.close()


def reset_tables(db_path: Path = DB_PATH) -> None:
    con = duckdb.connect(str(db_path))
    try:
        con.execute("DROP TABLE IF EXISTS cpi_append")
        con.execute("DROP TABLE IF EXISTS cpi_trunc")
        con.execute("DROP TABLE IF EXISTS cpi_inc")
        run_sql_script(con, "init_db.sql")
    finally:
        con.close()


def compare_final_state(db_path: Path = DB_PATH) -> dict:
    con = duckdb.connect(str(db_path))
    try:
        append_latest = con.execute("""
            WITH max_date AS (
                SELECT MAX(pull_date) AS pull_date
                FROM cpi_append
            )
            SELECT obs_date, cpi
            FROM cpi_append
            WHERE pull_date = (SELECT pull_date FROM max_date)
            ORDER BY obs_date
        """).fetchdf()

        trunc_df = con.execute("""
            SELECT obs_date, cpi
            FROM cpi_trunc
            ORDER BY obs_date
        """).fetchdf()

        inc_df = con.execute("""
            SELECT obs_date, cpi
            FROM cpi_inc
            ORDER BY obs_date
        """).fetchdf()

        return {
            "append_vs_trunc": append_latest.equals(trunc_df),
            "append_vs_inc": append_latest.equals(inc_df),
            "trunc_vs_inc": trunc_df.equals(inc_df),
            "append_rows": len(append_latest),
            "trunc_rows": len(trunc_df),
            "inc_rows": len(inc_df),
        }
    finally:
        con.close()


def simulate_daily_runs(
    start_date: str, end_date: str, db_path: Path = DB_PATH
) -> tuple[pd.DataFrame, dict]:
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    methods = ["append", "trunc", "inc"]

    timings = []

    for method in methods:
        reset_tables(db_path)

        t0 = time.perf_counter()
        for d in dates:
            load_method(method, d.strftime("%Y-%m-%d"), db_path=db_path)
        elapsed = time.perf_counter() - t0

        con = duckdb.connect(str(db_path))
        try:
            if method == "append":
                row_count = con.execute("SELECT COUNT(*) FROM cpi_append").fetchone()[0]
            elif method == "trunc":
                row_count = con.execute("SELECT COUNT(*) FROM cpi_trunc").fetchone()[0]
            else:
                row_count = con.execute("SELECT COUNT(*) FROM cpi_inc").fetchone()[0]
        finally:
            con.close()

        timings.append(
            {
                "method": method,
                "days_simulated": len(dates),
                "elapsed_seconds": elapsed,
                "final_row_count": row_count,
            }
        )

    # run once more in a shared db state for consistency check on the final day
    reset_tables(db_path)
    for d in dates:
        date_str = d.strftime("%Y-%m-%d")
        load_method("append", date_str, db_path=db_path)
        load_method("trunc", date_str, db_path=db_path)
        load_method("inc", date_str, db_path=db_path)

    consistency = compare_final_state(db_path)

    return pd.DataFrame(timings), consistency


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init")

    load_parser = subparsers.add_parser("load")
    load_parser.add_argument(
        "--method", required=True, choices=["append", "trunc", "inc"]
    )
    load_parser.add_argument("--pull-date", required=True)

    sim_parser = subparsers.add_parser("simulate")
    sim_parser.add_argument("--start-date", required=True)
    sim_parser.add_argument("--end-date", required=True)

    args = parser.parse_args()

    if args.command == "init":
        init_db()
        print("Database initialized.")

    elif args.command == "load":
        load_method(args.method, args.pull_date)
        print(f"Loaded method={args.method} for pull_date={args.pull_date}")

    elif args.command == "simulate":
        timing_df, consistency = simulate_daily_runs(args.start_date, args.end_date)
        print(timing_df)
        print(consistency)


if __name__ == "__main__":
    main()
