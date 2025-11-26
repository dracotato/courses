from bleach import clean
from flask import Blueprint, abort, g, json, redirect, render_template, request, url_for
from flask import current_app as ca
from markdown import markdown

from src.db import db_execute
from src.utils import EntityEnum, delete_entity, is_entity_owner, join_web
from src.views.auth import check_login

lesson_bp: Blueprint = Blueprint(
    "lesson",
    __name__,
    url_prefix="/lesson",
    template_folder=join_web("templates/lesson"),
)


lesson_bp.before_request(check_login)


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

        return redirect(url_for(".view", id=lesson_id))
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
        lesson_id=lesson["lessonid"],  # pyright: ignore
        is_owner=is_entity_owner(EntityEnum.LESSON, lesson["lessonid"]),  # pyright: ignore
    )


@lesson_bp.route("/<int:id>/", methods=["GET", "POST"])
def update(id: int):
    ownership = is_entity_owner(EntityEnum.LESSON, id)
    if ownership is None:  # lesson doesn't exist
        return abort(404)
    elif not ownership:
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

        return redirect(url_for(".view", id=id))
    else:
        return render_template(
            "editor.html",
            title="New Lesson",
            lesson_title=lesson["title"],  # pyright: ignore
            lesson_content=lesson["content"],  # pyright: ignore
        )


@lesson_bp.route("/", methods=["DELETE"])
def delete():
    body = request.json
    response = {}

    # one lesson
    if isinstance(body, int):
        response[str(body)] = delete_entity(EntityEnum.LESSON, body)
    # many lessons
    elif isinstance(body, list) and all([isinstance(x, int) for x in body]):
        for id in body:
            response[str(id)] = delete_entity(EntityEnum.LESSON, id)
    else:
        abort(400)  # bad request

    return json.jsonify(response)
