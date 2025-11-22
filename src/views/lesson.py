from bleach import clean
from flask import Blueprint, abort, g, redirect, render_template, request, url_for
from flask import current_app as ca
from markdown import markdown

from src.db import db_execute
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
        # TODO: remove this block after course routes are implemented
        if db_execute(query="SELECT count(*) FROM course", fetch_type=1) is not None:
            db_execute(
                query="INSERT INTO course (title,desc,owner) VALUES (?,?,?)",
                params=("default title", "default desc", 1),
                commit=True,
            )

        lesson_id = db_execute(
            query="INSERT INTO lesson (title, content, owner, course) VALUES (?,?,?,?)",
            params=(
                request.form["title"],
                request.form["content"],
                g.get("user")["userid"],
                1,
            ),
            commit=True,
            return_rowid=True,
        )

        return redirect(url_for("lesson.view", id=lesson_id))
    else:
        return render_template("editor.html", title="New Lesson")


@lesson_bp.route("/v/<int:id>/")
def view(id: int):
    lesson = db_execute(
        query="SELECT * FROM lesson WHERE lessonid = ?", params=(id,), fetch_type=1
    )

    if not lesson:
        abort(404)

    content = clean(
        markdown(lesson["content"]),  # pyright: ignore
        tags=ca.config["RENDER_TAGS"],
        attributes=ca.config["RENDER_ATTRS"],
    )

    return render_template(
        "render.html",
        title="View Lesson",
        lesson_title=lesson["title"],  # pyright: ignore
        content=content,
    )


@lesson_bp.route("/<int:id>/", methods=["GET", "POST"])
def update(id: int):
    if not is_owner(id):
        return abort(403)

    lesson = db_execute(
        "SELECT * FROM lesson where lessonid = ?", params=(id,), fetch_type=1
    )

    if request.method == "POST":
        db_execute(
            query="UPDATE lesson SET title = ?, content = ? WHERE lessonid = ?",
            params=(request.form["title"], request.form["content"], id),
            commit=True,
        )

        return redirect(url_for("lesson.view", id=id))
    else:
        return render_template(
            "editor.html",
            title="New Lesson",
            lesson_title=lesson["title"],  # pyright: ignore
            lesson_content=lesson["content"],  # pyright: ignore
        )


@lesson_bp.route("/<int:id>/", methods=["DELETE"])
def delete(id: int):
    if not is_owner(id):
        return abort(403)

    db_execute(query="DELETE FROM lesson WHERE lessonid = ?", params=(id,), commit=True)

    return abort(200)


# Helper functions
def is_owner(lesson_id: int):
    return (
        db_execute(
            query="SELECT owner FROM lesson WHERE lessonid = ?",
            params=(lesson_id,),
            fetch_type=1,
        )["owner"]  # pyright: ignore
        == g.get("user")["userid"]
    )
