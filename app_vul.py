from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# -----------------------------
# DATABASE SETUP
# -----------------------------
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    cur.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
    cur.execute("INSERT INTO users (username, password) VALUES ('bella', 'pass123')")
    conn.commit()
    conn.close()

init_db()

# -----------------------------
# HOME ROUTE
# -----------------------------
@app.route("/")
def home():
    return """
    <h2>Welcome to the Security Demo App</h2>
    <p><a href='/login'>Login Page (SQL Injection Demo)</a></p>
    <p><a href='/comment'>Comment Page (XSS Demo)</a></p>
    """

# -----------------------------
# 1. SQL INJECTION VULNERABILITY
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    html = """
    <h2>Login</h2>
    <form method="POST">
        Username: <input name="username"><br>
        Password: <input name="password"><br>
        <button type="submit">Login</button>
    </form>
    <p>{{message}}</p>
    """
    message = ""

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()

        # ❌ VULNERABLE QUERY
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        result = cur.execute(query).fetchone()

        if result:
            message = f"Welcome {result['username']}!"
        else:
            message = "Login failed"

    return render_template_string(html, message=message)

# -----------------------------
# 2. XSS VULNERABILITY
# -----------------------------
@app.route('/comment', methods=['GET', 'POST'])
def comment():
    html = """
    <h2>Leave a Comment</h2>
    <form method="POST">
        Comment: <input name="text">
        <button type="submit">Submit</button>
    </form>

    <p><strong>Last comment:</strong></p>
    <div>{{ comment|safe }}</div>
    """

    comment_text = ""

    if request.method == "POST":
        comment_text = request.form['text']  # ❌ UNSAFE

    return render_template_string(html, comment=comment_text)

if __name__ == "__main__":
    app.run(debug=True)
