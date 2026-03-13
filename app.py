import duckdb
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_FILE = "app.duckdb"


def get_connection():
    return duckdb.connect(DB_FILE)


@app.route("/")
def home():
    return jsonify({"message": "Flask API with DuckDB is running"})


@app.route("/shootings", methods=["GET"])
def get_shootings():
    limit = request.args.get("limit", default=10, type=int)

    con = get_connection()
    try:
        df = con.execute("SELECT * FROM shootings LIMIT ?", [limit]).fetchdf()
        return jsonify(df.to_dict(orient="records"))
    finally:
        con.close()


@app.route("/shootings/count", methods=["GET"])
def get_shootings_count():
    con = get_connection()
    try:
        count = con.execute("SELECT COUNT(*) FROM shootings").fetchone()[0]
        return jsonify({"shootings_count": count})
    finally:
        con.close()


@app.route("/users", methods=["GET"])
def get_users():
    con = get_connection()
    try:
        df = con.execute(
            "SELECT username, age, country FROM users ORDER BY username"
        ).fetchdf()
        return jsonify(df.to_dict(orient="records"))
    finally:
        con.close()


@app.route("/users", methods=["POST"])
def add_user():
    data = request.get_json()

    username = data.get("username")
    age = data.get("age")
    country = data.get("country")

    if not username or age is None or not country:
        return jsonify({"error": "username, age, and country are required"}), 400

    con = get_connection()
    try:
        existing = con.execute(
            "SELECT username FROM users WHERE username = ?", [username]
        ).fetchone()

        if existing:
            return jsonify({"error": "Username already exists"}), 400

        con.execute(
            "INSERT INTO users (username, age, country) VALUES (?, ?, ?)",
            [username, age, country],
        )

        return jsonify(
            {
                "message": "User added successfully",
                "user": {"username": username, "age": age, "country": country},
            }
        ), 201
    finally:
        con.close()


@app.route("/users/stats", methods=["GET"])
def get_user_stats():
    con = get_connection()
    try:
        total_users = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        avg_age = con.execute("SELECT AVG(age) FROM users").fetchone()[0]

        top_countries = con.execute("""
            SELECT country, COUNT(*) AS user_count
            FROM users
            GROUP BY country
            ORDER BY user_count DESC, country ASC
            LIMIT 3
        """).fetchall()

        return jsonify(
            {
                "number_of_users": total_users,
                "average_age": round(avg_age, 2) if avg_age is not None else None,
                "top_3_countries": [
                    {"country": row[0], "user_count": row[1]} for row in top_countries
                ],
            }
        )
    finally:
        con.close()


if __name__ == "__main__":
    app.run(debug=True)
