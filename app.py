from flask import Flask, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
app.secret_key = "spendly-secret-key-2026"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect("/profile")
    return render_template("landing.html")


@app.route("/register")
def register():
    if session.get("user_id"):
        return redirect("/")
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or not password:
        flash("All fields are required.", "error")
        return render_template("register.html")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone() is not None:
        conn.close()
        flash("Email already registered.", "error")
        return render_template("register.html")

    password_hash = generate_password_hash(password)
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    session["user_id"] = user_id
    return redirect("/profile")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect("/")
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("login.html")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    if not check_password_hash(row["password_hash"], password):
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    session["user_id"] = row["id"]
    return redirect("/profile")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/analytics")
def analytics():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("analytics.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")


def get_profile_date_filters(args):
    date_from = args.get("date_from")
    date_to = args.get("date_to")

    valid_from = None
    valid_to = None

    if date_from:
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            valid_from = date_from
        except ValueError:
            pass

    if date_to:
        try:
            datetime.strptime(date_to, "%Y-%m-%d")
            valid_to = date_to
        except ValueError:
            pass

    if valid_from and valid_to and valid_from > valid_to:
        flash("Start date must be before end date.", "error")
        valid_from = None
        valid_to = None

    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    this_month_start = today.replace(day=1).strftime("%Y-%m-%d")
    three_months_ago = (today - relativedelta(months=3)).strftime("%Y-%m-%d")
    six_months_ago = (today - relativedelta(months=6)).strftime("%Y-%m-%d")

    presets = {
        "this_month": (this_month_start, today_str),
        "three_months": (three_months_ago, today_str),
        "six_months": (six_months_ago, today_str),
        "all_time": (None, None)
    }

    return valid_from, valid_to, presets


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])
    if user is None:
        session.pop("user_id", None)
        return redirect(url_for("login"))

    valid_from, valid_to, presets = get_profile_date_filters(request.args)

    stats = get_summary_stats(session["user_id"], date_from=valid_from, date_to=valid_to)
    transactions = get_recent_transactions(session["user_id"], date_from=valid_from, date_to=valid_to)
    categories = get_category_breakdown(session["user_id"], date_from=valid_from, date_to=valid_to)

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
        date_from=valid_from,
        date_to=valid_to,
        presets=presets
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
