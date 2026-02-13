import os

import pandas as pd
from flask import Flask, Response, jsonify, request

app = Flask(__name__)

# ====== Paths ======
BASE_DIR = "/Users/dl/Desktop/Python/26spring-project/-Xingyi-Wang---Aileen--api"
DATA_PATH = os.path.join(BASE_DIR, "data", "NYPD_Shootings_20260213.csv")

ID_COL = "INCIDENT_KEY"

# ====== Load data once ======
df = pd.read_csv(DATA_PATH)


def df_to_csv_response(frame: pd.DataFrame) -> Response:
    csv_str = frame.to_csv(index=False)
    return Response(csv_str, mimetype="text/csv")


def df_to_json_response(frame: pd.DataFrame) -> Response:
    return jsonify(frame.to_dict(orient="records"))


def coerce_filter_value(series: pd.Series, raw: str):
    if pd.api.types.is_numeric_dtype(series):
        try:
            if "." in raw:
                return float(raw)
            return int(raw)
        except ValueError:
            return raw
    return raw


@app.route("/")
def welcome():
    return "<p>NYPD Shootings API by Xingyi Wang and Aileen Yang</p>"


@app.route("/sum", methods=["GET"])
def sum_route():
    a = request.args.get("a")
    b = request.args.get("b")
    if a is None or b is None:
        return jsonify({"error": "Missing query params: a and b"}), 400
    try:
        a_int = int(a)
        b_int = int(b)
    except ValueError:
        return jsonify({"error": "a and b must be integers"}), 400
    return jsonify({"a": a_int, "b": b_int, "sum": a_int + b_int})


@app.route("/factorial", methods=["GET"])
def factorial_route():
    n = request.args.get("n", default="10")
    try:
        n_int = int(n)
        if n_int < 0:
            return jsonify({"error": "n must be >= 0"}), 400
    except ValueError:
        return jsonify({"error": "n must be an integer"}), 400

    result = 1
    for i in range(2, n_int + 1):
        result *= i
    return jsonify({"n": n_int, "factorial": result})


@app.route("/api/list", methods=["GET"])
def list_records():
    """
    Query parameters:
      - format: json | csv
      - filterby (optional): column name
      - filtervalue (optional): value for filterby
      - limit (optional): default 100
      - offset (optional): default 0
    """
    out_format = request.args.get("format", default="json").lower()
    filterby = request.args.get("filterby")
    filtervalue = request.args.get("filtervalue")
    limit = request.args.get("limit")
    offset = request.args.get("offset")

    data = df

    # filtering
    if filterby is not None:
        if filterby not in df.columns:
            return jsonify({"error": f"Unknown column in filterby: {filterby}"}), 400
        if filtervalue is None:
            return jsonify(
                {"error": "filtervalue is required when filterby is provided"}
            ), 400

        col = data[filterby]
        val = coerce_filter_value(col, filtervalue)

        # strings: case-insensitive equality
        if pd.api.types.is_string_dtype(col) or col.dtype == object:
            data = data[col.astype(str).str.lower() == str(val).lower()]
        else:
            data = data[col == val]

    # pagination
    try:
        offset_i = int(offset) if offset is not None else 0
        limit_i = int(limit) if limit is not None else 100
        if offset_i < 0 or limit_i < 1:
            raise ValueError
    except ValueError:
        return jsonify(
            {"error": "limit must be >=1 and offset must be >=0 (integers)"}
        ), 400

    data = data.iloc[offset_i : offset_i + limit_i]

    # output
    if out_format == "csv":
        return df_to_csv_response(data)
    if out_format == "json":
        return df_to_json_response(data)
    return jsonify({"error": "format must be 'json' or 'csv'"}), 400


@app.route("/api/record/<int:incident_key>", methods=["GET"])
def get_record(incident_key: int):
    """
    Query parameters:
      - format: json | csv
    """
    out_format = request.args.get("format", default="json").lower()

    if ID_COL not in df.columns:
        return jsonify({"error": f"ID column not found in CSV: {ID_COL}"}), 500

    row = df[df[ID_COL] == incident_key]
    if row.empty:
        return jsonify({"error": "Record not found"}), 404

    if out_format == "csv":
        return df_to_csv_response(row)
    if out_format == "json":
        return df_to_json_response(row)
    return jsonify({"error": "format must be 'json' or 'csv'"}), 400


if __name__ == "__main__":
    app.run(debug=True)
