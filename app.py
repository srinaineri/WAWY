from flask import Flask, render_template, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "wawy_secret_key"
def create_database():
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

create_database()
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database/users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
          session["user"] = {
             "name": user[1],
             "email": user[2]
          }
          return redirect("/dashboard")
        else:
          return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database/users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    username = session["user"]["name"]
    email = session["user"]["email"]

    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT mood, created_at FROM mood_history WHERE user_id=? ORDER BY id DESC LIMIT 5",
        (email,)
    )

    moods = cursor.fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        username=username,
        moods=moods
    )
@app.route("/chat", methods=["GET", "POST"])
def chat():

    reply = ""

    if request.method == "POST":
        message = request.form["message"]

        reply = "You said: " + message

    return render_template("chat.html", reply=reply)
@app.route("/support")
def support():
    return render_template("support.html")
from datetime import datetime

def save_mood(mood):
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO mood_history (user_id, mood, created_at) VALUES (?, ?, ?)",
        (
            session["user"]["email"],
            mood,
            current_time
        )
    )

    conn.commit()
    conn.close()

@app.route("/happy")
def happy():
    save_mood("Happy")
    return render_template("happy.html")


@app.route("/sad")
def sad():
    save_mood("Sad")
    return render_template("sad.html")


@app.route("/stressed")
def stressed():
    save_mood("Stressed")
    return render_template("stressed.html")


@app.route("/lonely")
def lonely():
    save_mood("Lonely")
    return render_template("lonely.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)