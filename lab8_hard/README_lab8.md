# Lab 8: Loading Continuously Updated CPI Data into DuckDB

## Overview

This project implements three methods for loading continuously updated CPI vintage data into a DuckDB database:

- `append`
- `trunc`
- `inc` (incremental)

The source data is an Excel file of CPI vintages from the Philadelphia Federal Reserve. Each row is an observation month and each vintage column represents the value available in a particular release month.

The project is organized around one rule:

- all source-data access goes through `get_latest_data(pull_date)`

That function returns exactly two columns:

- `obs_date`
- `cpi`

All loading scripts use that output only.

---

## Project Structure

```text
lab8_hard/
├── data/
│   └── pcpiMvMd.xlsx
├── notebooks/
│   └── simulate_daily_runs.ipynb
├── scripts/
│   ├── init_db.sql
│   ├── load_append.sql
│   ├── load_trunc.sql
│   └── load_inc.sql
├── src/
│   └── cpi_pipeline.py
├── cpi.duckdb
└── README.md
```

---

## Expected Behavior of Each Table

### 1. `cpi_append`

This table stores a full snapshot for every run date.

Expected behavior:

- one row per `(pull_date, obs_date)`
- repeated runs for the same `pull_date` should not duplicate rows
- historical snapshots are preserved
- the same `obs_date` may appear many times with different `pull_date` values

What the user should expect to see:

- after running append for `2004-01-15`, all rows will have `pull_date = 2004-01-15`
- after running append again for `2004-02-15`, the table will contain both the `2004-01-15` snapshot and the `2004-02-15` snapshot

Use case:

- audit trail
- revision tracking over time

---

### 2. `cpi_trunc`

This table stores only the latest full snapshot.

Expected behavior:

- table is cleared before each run
- after each run, only the most recent snapshot remains
- no historical snapshots are kept

What the user should expect to see:

- after running trunc for `2004-01-15`, all rows will have `pull_date = 2004-01-15`
- after running trunc again for `2004-02-15`, the old rows are gone and only `pull_date = 2004-02-15` remains

Use case:

- current-state reporting
- simplest full-refresh workflow

---

### 3. `cpi_inc`

This table stores one current row per observation month.

Expected behavior:

- inserts new observations
- updates only changed values
- leaves unchanged rows untouched
- stores the date of the most recent update in `last_pull_date`

What the user should expect to see:

- exactly one row per `obs_date`
- after the first run, most rows will have the first run date as `last_pull_date`
- after a later run, only revised or newly available observations should show a newer `last_pull_date`

Use case:

- efficient maintenance of a current-state table

---

## Setup

Install dependencies in the virtual environment:

```bash
pip install duckdb pandas openpyxl jupyter matplotlib
```

---

## Usage

### Initialize the database

```bash
python src/cpi_pipeline.py init
```

This creates the tables:

- `cpi_append`
- `cpi_trunc`
- `cpi_inc`

---

### Load data with append

```bash
python src/cpi_pipeline.py load --method append --pull-date 2004-01-15
```

---

### Load data with trunc

```bash
python src/cpi_pipeline.py load --method trunc --pull-date 2004-01-15
```

---

### Load data with incremental

```bash
python src/cpi_pipeline.py load --method inc --pull-date 2004-01-15
```

---

### Simulate daily runs

```bash
python src/cpi_pipeline.py simulate --start-date 2004-01-01 --end-date 2004-03-31
```

This will:

- loop over the date range day by day
- run each loading strategy separately
- measure elapsed time
- compare final consistency across methods

---

## Manual Testing Instructions

### Test 1: Confirm `get_latest_data()` returns the right shape

In Python:

```python
from src.cpi_pipeline import get_latest_data

df = get_latest_data("2004-01-15")
print(df.head())
print(df.columns.tolist())
```

Expected:

- only two columns: `obs_date` and `cpi`
- no `DATE` column
- no vintage columns
- values should correspond to the latest vintage available by `2004-01-15`

---

### Test 2: Append method

Run:

```bash
python src/cpi_pipeline.py load --method append --pull-date 2004-01-15
python src/cpi_pipeline.py load --method append --pull-date 2004-02-15
python src/cpi_pipeline.py load --method append --pull-date 2004-02-15
```

Then inspect:

```python
import duckdb
con = duckdb.connect("cpi.duckdb")

con.execute("SELECT DISTINCT pull_date FROM cpi_append ORDER BY pull_date").fetchdf()
con.execute("SELECT * FROM cpi_append ORDER BY pull_date, obs_date LIMIT 20").fetchdf()
```

Expected:

- at least two pull dates: `2004-01-15` and `2004-02-15`
- rerunning the same date should not create duplicates

Optional duplicate check:

```python
con.execute("""
SELECT pull_date, obs_date, COUNT(*) AS n
FROM cpi_append
GROUP BY pull_date, obs_date
HAVING COUNT(*) > 1
""").fetchdf()
```

Expected:

- empty result

---

### Test 3: Trunc method

Run:

```bash
python src/cpi_pipeline.py load --method trunc --pull-date 2004-01-15
python src/cpi_pipeline.py load --method trunc --pull-date 2004-02-15
```

Then inspect:

```python
con.execute("SELECT DISTINCT pull_date FROM cpi_trunc").fetchdf()
con.execute("SELECT * FROM cpi_trunc ORDER BY obs_date LIMIT 20").fetchdf()
```

Expected:

- only one pull date remains
- that pull date should be `2004-02-15`

---

### Test 4: Incremental method

Run:

```bash
python src/cpi_pipeline.py load --method inc --pull-date 2004-01-15
python src/cpi_pipeline.py load --method inc --pull-date 2004-02-15
```

Then inspect:

```python
con.execute("SELECT * FROM cpi_inc ORDER BY obs_date LIMIT 20").fetchdf()
con.execute("""
SELECT last_pull_date, COUNT(*) AS n
FROM cpi_inc
GROUP BY last_pull_date
ORDER BY last_pull_date
""").fetchdf()
```

Expected:

- each `obs_date` appears once
- rows updated by the later run should have `last_pull_date = 2004-02-15`
- unchanged rows may keep `last_pull_date = 2004-01-15`

Optional uniqueness check:

```python
con.execute("""
SELECT obs_date, COUNT(*) AS n
FROM cpi_inc
GROUP BY obs_date
HAVING COUNT(*) > 1
""").fetchdf()
```

Expected:

- empty result

---

## Notebook Workflow

The notebook `notebooks/simulate_daily_runs.ipynb` should:

1. import the pipeline functions
2. reset tables
3. simulate daily runs over a date range
4. record elapsed time for each method
5. compare final consistency
6. display summary tables and a chart

Suggested first simulation range:

```python
timing_df, consistency = simulate_daily_runs(
    start_date="2004-01-01",
    end_date="2004-03-31"
)
```

A larger range can be used if runtime is acceptable.

---

## How to Interpret the Performance Comparison

### Consistency

The final contents of:

- the latest snapshot in `cpi_append`
- `cpi_trunc`
- `cpi_inc`

should match.

If the comparison returns `True` for all pairwise checks, the methods are consistent.

### Speed

Typical expectations:

- `append` may be slower over time because the table keeps growing
- `trunc` is simple but rewrites the whole table each run
- `inc` is usually the most efficient current-state strategy because it updates only changed rows

Actual results depend on date range, hardware, and DuckDB version.

---

## Deliverables

This submission includes:

- `src/cpi_pipeline.py`
- `scripts/init_db.sql`
- `scripts/load_append.sql`
- `scripts/load_trunc.sql`
- `scripts/load_inc.sql`
- `notebooks/simulate_daily_runs.ipynb`
- `README.md`

---

## Short Conclusion

This lab demonstrates how continuously updated economic data can be maintained in a database using three common loading strategies. The three methods produce the same final current-state data, but they differ in storage pattern, history retention, and runtime behavior. `append` is best for preserving historical snapshots, `trunc` is the simplest full refresh strategy, and `incremental` is best for efficient maintenance of the latest state.
