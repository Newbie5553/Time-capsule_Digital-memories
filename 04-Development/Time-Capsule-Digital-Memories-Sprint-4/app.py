"""Time Capsule Digital Memories Sprints 1–4: private memories, timed access, sharing and search."""

from contextlib import closing
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
import re
import secrets
import sqlite3

from flask import (
    Flask, abort, flash, g, jsonify, redirect, render_template,
    request, send_from_directory, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


def create_app(test_config=None):
    """Create and configure the application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(
        DATABASE=str(Path(app.instance_path) / "time_capsule_digital_memories.db"),
        SECRET_KEY=None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=50 * 1024 * 1024,
        UPLOAD_FOLDER=str(Path(app.instance_path) / "uploads"),
    )
    if test_config:
        app.config.update(test_config)

    # Preserve a previous installation when the branding changes the DB filename.
    # Only migrate a single database in this app's private instance directory.
    if not test_config or "DATABASE" not in test_config:
        target = Path(app.config["DATABASE"])
        if not target.exists() and target.parent.exists():
            existing = list(target.parent.glob("*.db"))
            if len(existing) == 1:
                # SQLite backup also safely includes any committed WAL contents.
                temporary = target.with_suffix(".migration.tmp")
                with closing(sqlite3.connect(existing[0])) as old_db:
                    with closing(sqlite3.connect(temporary)) as new_db:
                        old_db.backup(new_db)
                temporary.replace(target)
                existing[0].unlink()
            elif len(existing) > 1:
                raise RuntimeError(
                    "Several databases were found in instance. Back up the folder "
                    "and select the correct database before upgrading."
                )

    # Keep real account data and the signing key outside public static files.
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    if not app.config["SECRET_KEY"]:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        key_file = Path(app.instance_path) / "secret.key"
        if not key_file.exists():
            key_file.write_text(secrets.token_hex(32), encoding="utf-8")
        app.config["SECRET_KEY"] = key_file.read_text(encoding="utf-8")

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    def get_db():
        """Reuse one database connection during each request."""
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
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
        # Add Sprint 2 tables without removing Sprint 1 accounts.
        get_db().executescript("""
            CREATE TABLE IF NOT EXISTS capsules (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                theme TEXT NOT NULL DEFAULT 'sky',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY,
                capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                stored TEXT NOT NULL UNIQUE,
                kind TEXT NOT NULL
            );
        """)
        # Idempotent upgrade: keep all Sprint 1/2 accounts, drafts and files.
        columns = {row["name"] for row in get_db().execute("PRAGMA table_info(capsules)")}
        for name, definition in (
            ("locked", "INTEGER NOT NULL DEFAULT 0"),
            ("unlock_at", "REAL"),
            ("sealed_at", "REAL"),
        ):
            if name not in columns:
                get_db().execute(f"ALTER TABLE capsules ADD COLUMN {name} {definition}")
        # Sprint 4 is an additive migration; existing capsules and files stay intact.
        get_db().executescript("""
            CREATE TABLE IF NOT EXISTS capsule_shares (
                id INTEGER PRIMARY KEY,
                capsule_id INTEGER NOT NULL REFERENCES capsules(id) ON DELETE CASCADE,
                recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at REAL NOT NULL,
                UNIQUE(capsule_id, recipient_id)
            );
            CREATE INDEX IF NOT EXISTS idx_shares_recipient
                ON capsule_shares(recipient_id, capsule_id);
        """)
        get_db().commit()

    def now():
        # Injectable clock lets tests check the exact opening boundary.
        clock = app.config.get("CLOCK")
        return clock() if clock else datetime.now(timezone.utc).timestamp()

    def capsule_state(capsule):
        if not capsule["locked"]:
            return "draft"
        if capsule["unlock_at"] is None or now() < capsule["unlock_at"]:
            return "sealed"
        return "ready"

    @app.template_filter("date")
    def display_date(timestamp):
        return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%b %d, %Y")

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
            # Serialize state-changing capsule requests so an old editor cannot
            # overwrite a capsule that another tab just sealed.
            if g.user and request.endpoint in {"edit_capsule", "seal_capsule", "delete_capsule", "share_capsule", "revoke_share"}:
                get_db().execute("BEGIN IMMEDIATE")

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
                    flash("Your account is ready. Welcome to Time Capsule Digital Memories!", "success")
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

    def owned_capsule(capsule_id):
        """Check ownership for every read, update, delete, and file request."""
        capsule = get_db().execute(
            "SELECT * FROM capsules WHERE id = ? AND user_id = ?",
            (capsule_id, g.user["id"]),
        ).fetchone()
        if capsule is None:
            abort(404)
        return capsule

    def readable_capsule(capsule_id):
        """Read permission is separate from owner-only edit/share permissions."""
        capsule = get_db().execute(
            """SELECT c.*, u.name AS owner_name FROM capsules c
               JOIN users u ON u.id = c.user_id
               WHERE c.id = ? AND (
                   c.user_id = ? OR EXISTS (
                       SELECT 1 FROM capsule_shares s
                       WHERE s.capsule_id = c.id AND s.recipient_id = ?
                   )
               )""",
            (capsule_id, g.user["id"], g.user["id"]),
        ).fetchone()
        if capsule is None:
            abort(404)
        # Recheck time on every shared read, including file and status requests.
        if capsule["user_id"] != g.user["id"] and capsule_state(capsule) != "ready":
            abort(404)
        return capsule

    def shares_for(capsule_id):
        return get_db().execute(
            """SELECT s.id, s.created_at, u.name, u.email FROM capsule_shares s
               JOIN users u ON u.id = s.recipient_id
               WHERE s.capsule_id = ? ORDER BY s.created_at, s.id""",
            (capsule_id,),
        ).fetchall()

    def attachments_for(capsule_id):
        return get_db().execute(
            "SELECT * FROM attachments WHERE capsule_id = ? ORDER BY id",
            (capsule_id,),
        ).fetchall()

    def identify_upload(upload):
        """Check the extension and basic file header; this is not malware scanning."""
        extension = Path(upload.filename).suffix.lower()
        header = upload.stream.read(32)
        upload.stream.seek(0)
        matches = {
            ".jpg": header.startswith(b"\xff\xd8\xff"),
            ".jpeg": header.startswith(b"\xff\xd8\xff"),
            ".png": header.startswith(b"\x89PNG\r\n\x1a\n"),
            ".gif": header.startswith((b"GIF87a", b"GIF89a")),
            ".webp": header[:4] == b"RIFF" and header[8:12] == b"WEBP",
            ".mp4": header[4:8] == b"ftyp",
            ".webm": header.startswith(b"\x1a\x45\xdf\xa3"),
        }
        if not matches.get(extension, False):
            return None
        kind = "video" if extension in (".mp4", ".webm") else "image"
        return extension, kind

    @app.get("/dashboard")
    @login_required
    def dashboard():
        capsules = get_db().execute(
            """SELECT c.*, COUNT(a.id) AS file_count
               FROM capsules c LEFT JOIN attachments a ON a.capsule_id = c.id
               WHERE c.user_id = ? GROUP BY c.id
               ORDER BY c.updated_at DESC, c.id DESC""",
            (g.user["id"],),
        ).fetchall()
        # Never pass sealed messages to the dashboard template.
        cards = []
        for capsule in capsules:
            cards.append({
                key: capsule[key] for key in
                ("id", "title", "theme", "updated_at", "file_count", "unlock_at")
            })
            cards[-1]["state"] = capsule_state(capsule)
        counts = {state: sum(c["state"] == state for c in cards)
                  for state in ("draft", "sealed", "ready")}
        query = request.args.get("q", "").strip()
        if len(query) > 100:
            abort(400, "Search titles using at most 100 characters.")
        # Literal Unicode-aware matching: % and _ are ordinary characters.
        matches = [card for card in cards if query.casefold() in card["title"].casefold()]
        return render_template(
            "dashboard.html", capsules=matches, counts=counts, query=query,
            total_count=len(cards),
        )

    @app.get("/shared")
    @login_required
    def shared_capsules():
        query = request.args.get("q", "").strip()
        if len(query) > 100:
            abort(400, "Search titles using at most 100 characters.")
        rows = get_db().execute(
            """SELECT c.id, c.title, c.theme, c.locked, c.unlock_at,
                      c.updated_at, u.name AS owner_name, s.created_at AS shared_at
               FROM capsule_shares s JOIN capsules c ON c.id = s.capsule_id
               JOIN users u ON u.id = c.user_id
               WHERE s.recipient_id = ? ORDER BY s.created_at DESC, s.id DESC""",
            (g.user["id"],),
        ).fetchall()
        available = [c for c in rows if capsule_state(c) == "ready"]
        matches = [c for c in available if query.casefold() in c["title"].casefold()]
        return render_template(
            "shared.html", capsules=matches, query=query, total_count=len(available),
        )

    @app.route("/capsules/<int:capsule_id>/share", methods=["GET", "POST"])
    @login_required
    def share_capsule(capsule_id):
        capsule = owned_capsule(capsule_id)
        if capsule_state(capsule) != "ready":
            abort(403, "Only opened capsules can be shared.")
        email = ""
        error = None
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
                error = "Enter a valid registered email address."
            else:
                recipient = get_db().execute(
                    "SELECT id FROM users WHERE email = ?", (email,),
                ).fetchone()
                if recipient is None:
                    error = "No registered account matches that email. Ask them to register first."
                elif recipient["id"] == g.user["id"]:
                    error = "This is your own capsule. Choose another registered user."
                else:
                    try:
                        get_db().execute(
                            """INSERT INTO capsule_shares (capsule_id, recipient_id, created_at)
                               VALUES (?, ?, ?)""", (capsule_id, recipient["id"], now()),
                        )
                        get_db().commit()
                    except sqlite3.IntegrityError:
                        get_db().rollback()
                        error = "This capsule is already shared with that person."
                    else:
                        flash("Memory shared. They can find it in Shared with me.", "success")
                        return redirect(url_for("share_capsule", capsule_id=capsule_id))
            flash(error, "error")
        return render_template(
            "share.html", capsule=capsule, shares=shares_for(capsule_id), email=email,
        ), (400 if error else 200)

    @app.post("/capsules/<int:capsule_id>/shares/<int:share_id>/revoke")
    @login_required
    def revoke_share(capsule_id, share_id):
        capsule = owned_capsule(capsule_id)
        if capsule_state(capsule) != "ready":
            abort(403, "Sharing is available only after the opening time.")
        if request.form.get("confirm") != "revoke":
            abort(400, "Confirm removal of this person's access.")
        cursor = get_db().execute(
            "DELETE FROM capsule_shares WHERE id = ? AND capsule_id = ?",
            (share_id, capsule_id),
        )
        if cursor.rowcount != 1:
            abort(404)
        get_db().commit()
        flash("Access removed. Files already downloaded cannot be recalled.", "success")
        return redirect(url_for("share_capsule", capsule_id=capsule_id))

    @app.route("/capsules/new", methods=["GET", "POST"])
    @app.route("/capsules/<int:capsule_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_capsule(capsule_id=None):
        capsule = owned_capsule(capsule_id) if capsule_id else None
        if capsule and capsule["locked"]:
            abort(403, "A sealed capsule cannot be edited.")
        attachments = attachments_for(capsule_id) if capsule_id else []
        values = dict(capsule) if capsule else {"title": "", "message": "", "theme": "sky"}

        if request.method == "POST":
            values = {
                "title": request.form.get("title", "").strip(),
                "message": request.form.get("message", "").strip(),
                "theme": request.form.get("theme", "sky"),
            }
            uploads = [file for file in request.files.getlist("files") if file.filename]
            error = None
            if not 1 <= len(values["title"]) <= 100:
                error = "Add a title between 1 and 100 characters."
            elif not 1 <= len(values["message"]) <= 20000:
                error = "Add a message between 1 and 20,000 characters."
            elif values["theme"] not in ("sky", "rose", "forest"):
                error = "Choose one of the three cover colors."
            elif len(attachments) + len(uploads) > 10:
                error = "Each capsule can have up to 10 attachments in total."

            validated_uploads = []
            if error is None:
                for upload in uploads:
                    identified = identify_upload(upload)
                    if identified is None:
                        error = "Use a real JPG, PNG, GIF, WebP, MP4 or WebM file with its matching extension."
                        break
                    extension, kind = identified
                    validated_uploads.append((upload, extension, kind))

            if error:
                flash(error, "error")
                return render_template(
                    "editor.html", capsule=capsule, values=values, attachments=attachments,
                ), 400

            saved_paths = []
            try:
                timestamp = datetime.now(timezone.utc).timestamp()
                if capsule:
                    get_db().execute(
                        """UPDATE capsules SET title = ?, message = ?, theme = ?,
                           updated_at = ? WHERE id = ? AND user_id = ?""",
                        (values["title"], values["message"], values["theme"],
                         timestamp, capsule_id, g.user["id"]),
                    )
                else:
                    cursor = get_db().execute(
                        """INSERT INTO capsules
                           (user_id, title, message, theme, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (g.user["id"], values["title"], values["message"],
                         values["theme"], timestamp, timestamp),
                    )
                    capsule_id = cursor.lastrowid

                for upload, extension, kind in validated_uploads:
                    # Random disk names prevent collisions and path traversal.
                    stored_name = secrets.token_hex(24) + extension
                    original_name = secure_filename(upload.filename) or ("memory" + extension)
                    destination = Path(app.config["UPLOAD_FOLDER"]) / stored_name
                    saved_paths.append(destination)
                    upload.save(destination)
                    get_db().execute(
                        """INSERT INTO attachments (capsule_id, filename, stored, kind)
                           VALUES (?, ?, ?, ?)""",
                        (capsule_id, original_name, stored_name, kind),
                    )
                get_db().commit()
            except (OSError, sqlite3.Error):
                get_db().rollback()
                for path in saved_paths:
                    path.unlink(missing_ok=True)
                app.logger.exception("Could not save capsule draft")
                flash("We couldn’t save the draft. Check free disk space and try again.", "error")
                return render_template(
                    "editor.html", capsule=capsule, values=values, attachments=attachments,
                ), 500

            flash("Your draft is saved. You can return and edit it anytime.", "success")
            return redirect(url_for("view_capsule", capsule_id=capsule_id))

        return render_template(
            "editor.html", capsule=capsule, values=values, attachments=attachments,
        )

    @app.get("/capsules/<int:capsule_id>")
    @login_required
    def view_capsule(capsule_id):
        capsule = readable_capsule(capsule_id)
        state = capsule_state(capsule)
        if state == "sealed":
            metadata = {key: capsule[key] for key in ("id", "title", "theme", "unlock_at")}
            return render_template("locked.html", capsule=metadata)
        return render_template(
            "capsule.html", capsule=capsule, attachments=attachments_for(capsule_id), state=state,
            is_owner=capsule["user_id"] == g.user["id"],
        )

    @app.get("/attachments/<int:attachment_id>")
    @login_required
    def download_attachment(attachment_id):
        attachment = get_db().execute(
            "SELECT * FROM attachments WHERE id = ?", (attachment_id,),
        ).fetchone()
        if attachment is None:
            abort(404)
        capsule = readable_capsule(attachment["capsule_id"])
        if capsule_state(capsule) == "sealed":
            abort(403, "This attachment is sealed until the opening time.")
        return send_from_directory(
            app.config["UPLOAD_FOLDER"], attachment["stored"],
            as_attachment=True, download_name=attachment["filename"],
        )

    @app.route("/capsules/<int:capsule_id>/delete", methods=["GET", "POST"])
    @login_required
    def delete_capsule(capsule_id):
        capsule = owned_capsule(capsule_id)
        if capsule["locked"]:
            abort(403, "Only unsealed drafts can be deleted.")
        if request.method == "GET":
            return render_template("delete_capsule.html", capsule=capsule)

        if request.form.get("confirm") != "delete":
            abort(400, "Confirm deletion before removing this draft.")
        files = attachments_for(capsule_id)
        get_db().execute("DELETE FROM capsules WHERE id = ?", (capsule_id,))
        get_db().commit()  # Foreign-key cascade removes the attachment records.
        for attachment in files:
            try:
                (Path(app.config["UPLOAD_FOLDER"]) / attachment["stored"]).unlink(missing_ok=True)
            except OSError:
                # The deleted draft cannot be downloaded even if disk cleanup fails.
                app.logger.exception("Could not remove an orphaned attachment from disk")
        flash("Draft deleted.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/capsules/<int:capsule_id>/seal", methods=["GET", "POST"])
    @login_required
    def seal_capsule(capsule_id):
        capsule = owned_capsule(capsule_id)
        if capsule["locked"]:
            abort(403, "This capsule has already been sealed.")
        if request.method == "POST":
            error = None
            try:
                selected = datetime.fromisoformat(request.form.get("unlock_at", "").replace("Z", "+00:00"))
                if selected.tzinfo is None:
                    raise ValueError("Timezone required")
                unlock_at = selected.timestamp()
                if unlock_at <= now():
                    error = "Choose an opening date and time in the future."
            except (ValueError, OverflowError, OSError):
                error = "Select a valid opening date and time."
            if request.form.get("confirm") != "seal":
                error = "Confirm that you want to seal this capsule."
            if error:
                flash(error, "error")
                return render_template("seal_capsule.html", capsule=capsule), 400
            timestamp = now()
            get_db().execute(
                """UPDATE capsules SET locked = 1, unlock_at = ?, sealed_at = ?,
                   updated_at = ? WHERE id = ? AND user_id = ? AND locked = 0""",
                (unlock_at, timestamp, timestamp, capsule_id, g.user["id"]),
            )
            get_db().commit()
            flash("Sealed with care. Your memories will open when the time is right.", "success")
            return redirect(url_for("view_capsule", capsule_id=capsule_id))
        return render_template("seal_capsule.html", capsule=capsule)

    @app.get("/capsules/<int:capsule_id>/status")
    @login_required
    def capsule_status(capsule_id):
        capsule = readable_capsule(capsule_id)
        # Metadata only. The browser clock never grants permission to read files.
        return jsonify(
            state=capsule_state(capsule),
            server_now=now(),
            unlock_at=capsule["unlock_at"],
        )

    @app.errorhandler(403)
    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(413)
    def show_error(error):
        return render_template("error.html", error=error), error.code

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
