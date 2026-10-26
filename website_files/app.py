"""
Moffat Bay Lodge - login and registration (no JavaScript needed).
Run with:  python app.py   then open http://localhost:5000
"""
import os
from datetime import date
from functools import wraps
from urllib.parse import quote

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, session
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


# ---------------------------------------------------------------- helpers
def query(sql, params=()):
    """Run a SELECT and return all rows as dictionaries"""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        db.close()


def login_required(view):
    """Send logged-out visitors to the login page, then bring them back"""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "customer_id" not in session:
            return redirect("/login?next=" + quote(request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return wrapped


def safe_next(value):
    """Only allow redirects to pages on this site"""
    return value if value.startswith("/") and not value.startswith("//") else "/"


# ---------------------------------------------------------------- pages
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------- About
@app.route("/about")
@app.route("/about.html")
def about_page():
    return render_template("about.html")


# ---------------------------------------------------------------- lodge
@app.route("/lodge")
@app.route("/lodge.html")
def lodge_page():
    return render_template("lodge.html")


@app.route("/login")
@app.route("/login.html")
def login_page():
    return render_template("login.html")


# ---------------------------------------------------------------- booking
def render_booking(lodge_id, error=None):
    lodges = query("SELECT lodge_id, lodge_name, lodge_description, lodge_image FROM Lodge WHERE lodge_id = %s",
        (lodge_id,))
    if not lodges:
        abort(404)
    rooms = query("SELECT room_type_id, room_size, nightly_rate FROM Room_Type ORDER BY nightly_rate")
    return render_template("lodge-reservation.html", lodge=lodges[0], rooms=rooms,
        today=date.today().isoformat(), error=error, form=request.form)


@app.route("/lodge-reservation", methods=["GET", "POST"])
@app.route("/lodge-reservation.html", methods=["GET", "POST"])
@login_required
def lodge_reservation():
    lodge_id = request.args.get("lodge", type=int)
    if not lodge_id:
        return redirect("/lodge")
    if request.method == "GET":
        return render_booking(lodge_id)
    
    try:
        room_type_id = int(request.form["room_type_id"])
        guests = int(request.form["guests"])
        check_in = date.fromisoformat(request.form["check_in"])
        check_out = date.fromisoformat(request.form["check_out"])
    except (KeyError, ValueError):
        return render_booking(lodge_id, "Please choose your dates, room, and number of guests.")
    if check_in < date.today() or check_out <= check_in:
        return render_booking(lodge_id, "Please choose valid dates (departure must be after arrival).")
    if not 1 <= guests <= 4:
        return render_booking(lodge_id, "Please choose between 1 and 4 guests.")
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("SELECT lodge_id FROM Lodge WHERE lodge_id = %s FOR UPDATE", (lodge_id,))
        if not cur.fetchone():
            abort(404)
        
        cur.execute("SELECT nightly_rate FROM Room_Type WHERE room_type_id = %s", (room_type_id,))
        room = cur.fetchone()
        if not room:
            return render_booking(lodge_id, "Please choose a room.")
        
        cur.execute("SELECT 1 FROM Reservation WHERE lodge_id = %s AND room_type_id = %s "
            "AND check_in_date < %s AND check_out_date > %s LIMIT 1",
            (lodge_id, room_type_id, check_out, check_in))
        if cur.fetchone():
            return render_booking(lodge_id, "Sorry, that room is already booked for those dates.")
        
        total = room["nightly_rate"] * (check_out - check_in).days
        cur.execute("INSERT INTO Reservation (customer_id, lodge_id, room_type_id, number_of_guests, "
            "check_in_date, check_out_date, total_cost) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (session["customer_id"], lodge_id, room_type_id, guests, check_in, check_out, total))
        db.commit()
        new_id = cur.lastrowid
    finally:
        cur.close()
        db.close()
    
    return redirect(f"/reservation-summary/{new_id}")
    
# ---------------------------------------------------------------- reservation summary
@app.route("/reservation-summary/<int:reservation_id>")
@login_required
def reservation_summary(reservation_id):

    reservations = query("""
        SELECT
            r.reservation_id,
            r.customer_id,
            r.number_of_guests,
            r.check_in_date,
            r.check_out_date,
            r.total_cost,

            c.first_name,
            c.last_name,

            l.lodge_name,
            l.lodge_description,
            l.lodge_image,

            rt.room_size,
            rt.nightly_rate

        FROM Reservation r

        JOIN Customer c
            ON r.customer_id = c.customer_id

        JOIN Lodge l
            ON r.lodge_id = l.lodge_id

        JOIN Room_Type rt
            ON r.room_type_id = rt.room_type_id

        WHERE r.reservation_id = %s
          AND r.customer_id = %s
    """, (reservation_id, session["customer_id"]))

    if not reservations:
        abort(404)

    reservation = reservations[0]

    nights = (
        reservation["check_out_date"]
        - reservation["check_in_date"]
    ).days

    return render_template(
        "reservation-summary.html",
        reservation=reservation,
        nights=nights
    )    
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
