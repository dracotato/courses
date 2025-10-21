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

from src.db import get_db
from src.utils import join_web

lesson_bp: Blueprint = Blueprint(
    "lesson",
    __name__,
    url_prefix="/lesson",
    template_folder=join_web("templates/lesson"),
)


@lesson_bp.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        db = get_db()

        # automatically create a test user, and course
        # TODO: remove this block after user routes are implemented
        cur = db.execute("SELECT count(*) FROM user;")
        if cur.fetchone()["count(*)"] == 0:
            cur.execute(
                "INSERT INTO user (username,email,password) VALUES (?,?,?)",
                ("default", "default@courses.com", "pass"),
            )
        # TODO: remove this block after course routes are implemented
        cur.execute("SELECT count(*) FROM course;")
        if cur.fetchone()["count(*)"] == 0:
            cur.execute(
                "INSERT INTO course (title,desc,owner) VALUES (?,?,?)",
                ("default title", "default desc", 1),
            )

        cur.execute(
            "INSERT INTO lesson (title, content, owner, course) VALUES (?,?,?,?)",
            (request.form["title"], request.form["content"], 1, 1),
        )
        db.commit()

        return redirect(url_for("lesson.view", id=cur.lastrowid))
    else:
        return render_template("editor.html", title="New Lesson")


@lesson_bp.route("/v/<int:id>/")
def view(id: int):
    cur = get_db().execute("SELECT * FROM lesson WHERE lessonid = ?", (id,))
    lesson = cur.fetchone()

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
