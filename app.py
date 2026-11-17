import os
import time

import pymysql
from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Message Board</title></head>
<body>
  <h1>Message Board</h1>
  <form method="post" action="/add">
    <input name="body" maxlength="255" placeholder="Write a message" required>
    <button type="submit">Add</button>
  </form>
  <ul>
    {% for m in messages %}
      <li>{{ m.body }} <small>({{ m.created_at }})</small></li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def get_conn():
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "appuser"),
        password=os.environ.get("DB_PASSWORD", "changeme"),
        database=os.environ.get("DB_NAME", "appdb"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def init_db():
    # Retry so the app survives starting before MySQL is fully ready
    for _ in range(30):
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS messages ("
                    "id INT AUTO_INCREMENT PRIMARY KEY, "
                    "body VARCHAR(255) NOT NULL, "
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                )
            conn.commit()
            conn.close()
            return
        except pymysql.err.OperationalError:
            time.sleep(2)
    raise RuntimeError("Could not connect to the database")


init_db()


@app.route("/")
def index():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT body, created_at FROM messages ORDER BY id DESC LIMIT 50")
        messages = cur.fetchall()
    conn.close()
    return render_template_string(PAGE, messages=messages)


@app.route("/add", methods=["POST"])
def add():
    body = request.form.get("body", "").strip()[:255]
    if body:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (body) VALUES (%s)", (body,))
        conn.commit()
        conn.close()
    return redirect("/")


@app.route("/health")
def health():
    return {"status": "ok"}
