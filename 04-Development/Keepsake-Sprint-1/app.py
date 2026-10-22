"""Keepsake Sprint 1: accounts, welcome page, and basic dashboard."""

from functools import wraps
from pathlib import Path
import re
import secrets
import sqlite3

from flask import (
    Flask, abort, flash, g, redirect, render_template,
    request, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(test_config=None):
    """Create and configure the application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        DATABASE=str(Path(app.instance_path) / "keepsake.db"),
        SECRET_KEY=None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    # Keep real account data and the signing key outside public static files.
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    if not app.config["SECRET_KEY"]:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        key_file = Path(app.instance_path) / "secret.key"
        if not key_file.exists():
            key_file.write_text(secrets.token_hex(32), encoding="utf-8")
        app.config["SECRET_KEY"] = key_file.read_text(encoding="utf-8")

    def get_db():
        """Reuse one database connection during each request."""
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error=None):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    with app.app_context():
        get_db().execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        get_db().commit()

    def csrf_token():
        """Provide a token that forms must submit with every POST request."""
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(24)
        return session["csrf"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def load_user_and_check_form():
        g.user = get_db().execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (session.get("user_id"),),
        ).fetchone()

        if request.method == "POST":
            expected = session.get("csrf", "")
            received = request.form.get("csrf", "")
            if not expected or not secrets.compare_digest(
                expected.encode(), received.encode()
            ):
                abort(400, "Your form expired. Refresh the page and try again.")

    @app.after_request
    def set_response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        return response

    def login_required(view):
        """Prevent visitors from opening pages that require an account."""
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped_view

    @app.get("/")
    def home():
        if g.user:
            return redirect(url_for("dashboard"))
        return render_template("welcome.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Validate account details, hash the password, and save the user."""
        if g.user:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not name or len(name) > 60:
                flash("Enter a name between 1 and 60 characters.", "error")
            elif len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
                flash("Enter a valid email address.", "error")
            elif not 8 <= len(password) <= 256:
                flash("Use a password between 8 and 256 characters.", "error")
            else:
                password_hash = generate_password_hash(password)
                try:
                    cursor = get_db().execute(
                        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                        (name, email, password_hash),
                    )
                    get_db().commit()
                except sqlite3.IntegrityError:
                    get_db().rollback()
                    flash("This email already has an account. Please sign in.", "error")
                else:
                    session.clear()
                    session["user_id"] = cursor.lastrowid
                    flash("Your account is ready. Welcome to Keepsake!", "success")
                    return redirect(url_for("dashboard"))

        return render_template("auth.html", register=True)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Check credentials and start a signed user session."""
        if g.user:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = get_db().execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

            if user and check_password_hash(user["password"], password):
                session.clear()
                session["user_id"] = user["id"]
                return redirect(url_for("dashboard"))

            flash("Email or password is incorrect.", "error")

        return render_template("auth.html", register=False)

    @app.post("/logout")
    @login_required
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.get("/dashboard")
    @login_required
    def dashboard():
        # Sprint 1 ends at the personal workspace; capsule features come later.
        return render_template("dashboard.html")

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def show_error(error):
        return render_template("error.html", error=error), error.code

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
