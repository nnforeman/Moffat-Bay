"""
Moffat Bay Lodge - login and registration (no JavaScript needed).
Run with:  python app.py   then open http://localhost:5000
"""
import os

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()  # reads your .env file

app = Flask(__name__, template_folder=".")
app.secret_key = os.getenv("SECRET_KEY")  # used to sign the login cookie


def get_db():
    """Open a connection to MySQL using the settings in .env"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


# ---------------------------------------------------------------- pages
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------- lodge
@app.route("/lodge")
@app.route("/lodge.html")
def lodge_page():
    return render_template("lodge.html")


@app.route("/login")
@app.route("/login.html")
def login_page():
    return render_template("login.html")


# ---------------------------------------------------------------- register
@app.route("/register", methods=["POST"])
def register():
    first = request.form.get("first_name", "").strip()
    last = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("telephone", "").strip()
    password = request.form.get("password", "")

    def fail(message):
        # show the login page again with the error (and keep what they typed)
        return render_template("login.html", register_error=message, form=request.form)

    if not first or not last or not email or not phone:
        return fail("Please fill in every field.")
    if "@" not in email:
        return fail("Please enter a valid email address.")
    if sum(c.isdigit() for c in phone) < 10:
        return fail("Please enter a valid phone number, for example 314-555-0101.")
    if len(password) < 8:
        return fail("Your password must be at least 8 characters.")

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Customer (first_name, last_name, email, telephone, password) "
            "VALUES (%s, %s, %s, %s, %s)",
            (first, last, email, phone, generate_password_hash(password)),
        )
        db.commit()
        new_id = cursor.lastrowid
    except mysql.connector.IntegrityError:  # the email column is UNIQUE
        return fail("An account with that email already exists.")
    finally:
        cursor.close()
        db.close()

    session["customer_id"] = new_id
    session["first_name"] = first
    return redirect("/")


# ---------------------------------------------------------------- login / logout
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT customer_id, first_name, password FROM Customer WHERE email = %s", (email,))
    customer = cursor.fetchone()
    cursor.close()
    db.close()

    # The second check lets the plain-text sample customers from the SQL file log in too.
    if not customer or not (
        check_password_hash(customer["password"], password) or customer["password"] == password
    ):
        return render_template("login.html", login_error="That email and password don't match.")

    session["customer_id"] = customer["customer_id"]
    session["first_name"] = customer["first_name"]
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------------------------------------------------------- other website files
# Serves styles.css, images and the other pages that sit next to app.py (but never app.py or .env)
@app.route("/<path:filename>")
def website_files(filename):
    if filename.endswith((".html", ".css", ".js", ".jpg", ".jpeg", ".png")):
        return send_from_directory(app.root_path, filename)
    abort(404)


if __name__ == "__main__":
    app.run(debug=True)
