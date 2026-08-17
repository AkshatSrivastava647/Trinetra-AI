from flask import Flask, request
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "units.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    cur.execute("SELECT COUNT(*) FROM units")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO units (name, location, status) VALUES (?, ?, ?)",
            [
                ("Alpha", "Sector 7", "Active"),
                ("Bravo", "Sector 3", "Standby"),
                ("Charlie", "Sector 12", "Active"),
            ],
        )
    conn.commit()
    conn.close()


@app.route("/unit/search")
def search():
    name = request.args.get("name", "")

    # VULNERABLE: raw string concatenation into SQL. This is the exact
    # flaw class Trinetra is built to find and fix -- don't copy this
    # pattern anywhere else.
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = f"SELECT id, name, location, status FROM units WHERE name = '{name}'"
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No units found."
    return "<br>".join(f"{r[1]} — {r[2]} — {r[3]}" for r in rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000, use_reloader=False)