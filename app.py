from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

# -------- DATABASE CONNECTION --------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Preethi@2006",
        database="smart_notes"
    )

# -------- LOGIN --------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")

    return render_template("login.html")

# -------- REGISTER --------
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (%s, %s)",
        (username, password)
    )
    conn.commit()
    conn.close()

    return redirect("/")

# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM notes WHERE user_id=%s ORDER BY created_at DESC",
        (session["user_id"],)
    )
    notes = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", notes=notes)

# -------- ADD NOTE --------
@app.route("/add", methods=["POST"])
def add_note():
    content = request.form["content"]
    category = request.form["category"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO notes (content, category, user_id) VALUES (%s, %s, %s)",
        (content, category, session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -------- DELETE NOTE --------
@app.route("/delete/<int:id>")
def delete_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM notes WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -------- PIN NOTE --------
@app.route("/pin/<int:id>")
def pin_note(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE notes SET pinned = NOT pinned WHERE id=%s",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect("/dashboard")

# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------- RUN --------
if __name__ == "__main__":
    app.run(debug=True, port=5000)