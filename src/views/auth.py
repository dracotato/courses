import functools
from re import fullmatch

from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from src.db import db_execute
from src.utils import join_web

auth_bp: Blueprint = Blueprint(
    "auth", __name__, url_prefix="/auth", template_folder=join_web("templates/auth")
)


# called before each request
def load_user():
    session_id = session.get("session_id")
    if session_id:
        user_session = db_execute(
            "SELECT * FROM session WHERE sessionid = ?",
            params=(session_id,),
            fetch_type=1,
        )
        if not user_session:  # invalid local session
            session.pop("session_id", None)
            return redirect(url_for(".login"))

        g.user = db_execute(
            "SELECT * FROM user WHERE userid = ?",
            params=(user_session["user"],),  # pyright: ignore
            fetch_type=1,
        )


# these are supposed to be ran before each request
def check_login():
    if not g.get("user"):
        # remember this page to come back after logging in
        session["prev_location"] = request.url
        return redirect(url_for(".login"))


def check_logout():
    if g.get("user"):
        return redirect(url_for("root.index"))


def logged_in(view):
    """Decorates a view to allow access to logged-in users only."""

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if g.get("user"):
            return view(*args, **kwargs)
        else:
            return redirect(url_for(".login"))

    return wrapper


def logged_out(view):
    "Decorates a view to allow access to logged-out users only."

    @functools.wraps(view)
    def wrapper(*args, **kwargs):
        if not g.get("user"):
            return view(*args, **kwargs)
        else:
            return redirect(url_for("root.index"))

    return wrapper


@auth_bp.route("/register/", methods=["GET", "POST"])
@logged_out
def register():
    if request.method == "POST":
        formdata = request.form
        valid = True

        # validity checks
        if not all(formdata):  # prevents any optional fields
            valid = False
        if not fullmatch(r"[a-zA-Z0-9]+", formdata["username"]):
            valid = False
        if not fullmatch(
            r"[a-zA-Z0-9-.]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+", formdata["email"]
        ):
            valid = False
        if len(formdata["password"]) < 8:
            valid = False
        if formdata["password"] != formdata["confirm-password"]:
            valid = False
        if db_execute(
            "SELECT * FROM user WHERE username = ?",
            params=(formdata["username"],),
            fetch_type=1,
        ):
            valid = False
        if db_execute(
            "SELECT * FROM user WHERE email = ?",
            params=(formdata["email"],),
            fetch_type=1,
        ):
            valid = False

        if valid:
            db_execute(
                "INSERT INTO user(username,email,password) VALUES (?,?,?)",
                params=(
                    formdata["username"],
                    formdata["email"],
                    generate_password_hash(formdata["password"]),
                ),
                commit=True,
            )
            return redirect(url_for(".login"))

    return render_template("register.html", title="Register")


@auth_bp.route("/login/", methods=["GET", "POST"])
@logged_out
def login():
    if request.method == "POST":
        formdata = request.form

        result = db_execute(
            "SELECT * FROM user WHERE username = :cred OR email = :cred",
            params={"cred": formdata["cred"]},
            fetch_type=1,
        )

        if not result:
            return "error in email or password."

        if check_password_hash(result["password"], formdata["password"]):  # pyright: ignore
            session["session_id"] = db_execute(
                "INSERT INTO session(useragent,user) VALUES (?,?)",
                params=(request.user_agent.string, result["userid"]),  # pyright: ignore
                commit=True,
                return_rowid=True,
            )
            prev_location = session.get("prev_location")
            if prev_location:
                session.pop("prev_location", None)
                return redirect(prev_location)
            return redirect(url_for("root.index"))

    return render_template("login.html", title="Login")


@auth_bp.route("/logout/", methods=["GET"])
def logout():
    if session["session_id"]:
        db_execute(
            "DELETE FROM session WHERE sessionid = ?",
            params=(session["session_id"],),
            commit=True,
        )
        session.pop("session_id", None)

    return redirect(url_for(".login"))
