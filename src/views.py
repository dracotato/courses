from bleach import clean
from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)
from flask import (
    current_app as ca,
)
from markdown import markdown

from .db import get_db, query_db

lesson_bp = Blueprint("lessons", __name__, url_prefix="/lessons")


def register_blueprints(app):
    app.register_blueprint(lesson_bp)


@lesson_bp.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        db = get_db()
        cur = db.execute(
            "INSERT INTO lesson (title, content) VALUES (?, ?)",
            (request.form["title"], request.form["content"]),
        )
        db.commit()

        return redirect(url_for("lessons.view", id=cur.lastrowid))
    else:
        return render_template("editor.html")


@lesson_bp.route("/<int:id>")
def view(id: int):
    lesson = query_db("SELECT * FROM lesson WHERE id = ?", args=(id,), one=True)

    if not lesson:
        abort(404)

    title = lesson["title"]  # pyright: ignore
    content = clean(
        markdown(lesson["content"]),  # pyright: ignore
        tags=ca.config["RENDER_TAGS"],
        attributes=ca.config["RENDER_ATTRS"],
    )

    return render_template("render.html", title=title, content=content)
