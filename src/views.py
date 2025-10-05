from bleach import clean
from flask import (
    Blueprint,
    Flask,
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

root_bp: Blueprint = Blueprint("root", __name__)
lesson_bp: Blueprint = Blueprint("lessons", __name__, url_prefix="/lessons")


def register_blueprints(app: Flask):
    for bp in [root_bp, lesson_bp]:
        app.register_blueprint(bp)


@root_bp.route("/")
def index():
    return "Welcome Home!"


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
        return render_template("editor.html", title="New Lesson")


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

    return render_template(
        "render.html", title="View Lesson", lesson_title=title, content=content
    )
