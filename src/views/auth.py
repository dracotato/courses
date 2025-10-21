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

from src.db import get_db
from src.utils import join_web

auth_bp: Blueprint = Blueprint(
    "auth", __name__, url_prefix="/auth", template_folder=join_web("templates/auth")
)


def load_user():
    user_id = session.get("user_id")
    if user_id:
        user = (
            get_db().execute("SELECT * FROM user WHERE userid = ?", (user_id,))
        ).fetchone()
        g.user = user


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        formdata = request.form
        print(formdata)
        valid = True

        # validity checks
        if not all(formdata):
            valid = False
            print("Null")
        if not fullmatch(r"[a-zA-Z0-9]+", formdata["username"]):
            valid = False
            print("Username")
        if not fullmatch(
            r"[a-zA-Z0-9-.]+@[a-zA-Z0-9]+\.[a-zA-Z0-9]+", formdata["email"]
        ):
            valid = False
            print("Email")
        if len(formdata["password"]) < 8:
            valid = False
            print("Password")
        if formdata["password"] != formdata["confirm-password"]:
            valid = False
            print("Inequal")
        if db.execute(
            "SELECT * FROM user WHERE username = ?", (formdata["username"],)
        ).fetchone():
            valid = False
            print("Username exists")
        if db.execute(
            "SELECT * FROM user WHERE email = ?", (formdata["email"],)
        ).fetchone():
            valid = False
            print("Email exists")

        if valid:
            db.execute(
                "INSERT INTO user(username,email,password) VALUES (?,?,?)",
                (
                    formdata["username"],
                    formdata["email"],
                    generate_password_hash(formdata["password"]),
                ),
            )
            db.commit()
            return redirect(url_for("auth.login"))

    return render_template("register.html", title="Register")


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        formdata = request.form

        result = db.execute(
            "SELECT * FROM user WHERE username = :cred OR email = :cred",
            {"cred": formdata["cred"]},
        ).fetchone()

        if check_password_hash(result["password"], formdata["password"]):
            session["user_id"] = result["userid"]
            return redirect(url_for("root.index"))

    return render_template("login.html", title="Login")
