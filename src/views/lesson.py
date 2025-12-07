from bleach import clean
from flask import (
    Blueprint,
    abort,
    flash,
    g,
    json,
    redirect,
    render_template,
    request,
    url_for,
)
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
    form = request.form
    if request.method == "POST":
        if (
            db_execute(
                query="SELECT * FROM course WHERE courseid = ? AND owner = ?",
                params=(form["course"], g.get("user")["userid"]),
                fetch_type=1,
            )
            and form["title"]
            and form["content"]
        ):
            db_execute(
                query="INSERT INTO lesson (title, content, owner, course) VALUES (?,?,?,?)",
                params=(
                    form["title"].strip(),
                    form["content"].strip(),
                    g.get("user")["userid"],
                    form["course"],
                ),
                commit=True,
                return_rowid=True,
            )
            flash("Lesson created.")
            if form["batch"] == "0":
                return redirect(url_for("root.course.view", id=form["course"]))
        else:
            return abort(400)

    owned_courses = db_execute(
        query="SELECT * FROM course WHERE owner = ?",
        params=(g.get("user")["userid"],),
        fetch_type=3,
    )
    if not owned_courses:
        flash("Please create a course first.")
        return redirect(url_for("root.course.create"))
    return render_template(
        "editor.html",
        title="New Lesson",
        owned_courses=owned_courses,
        # set course to same course from last request for batch writes
        courseid=form.get("course"),
    )


@lesson_bp.route("/v/<int:id>/")
def view(id: int):
    lesson = db_execute(
        query="SELECT * FROM lesson WHERE lessonid = ?", params=(id,), fetch_type=1
    )
    course = db_execute(
        query="SELECT * FROM course WHERE courseid = ?",
        params=(lesson["course"],),  # pyright: ignore
        fetch_type=1,
    )

    if not lesson:
        abort(404)

    # render markdown to html
    rendered_content = clean(
        markdown(lesson["content"]),  # pyright: ignore
        tags=ca.config["RENDER_TAGS"],
        attributes=ca.config["RENDER_ATTRS"],
    )

    return render_template(
        "render.html",
        title="View Lesson",
        course=course,
        lesson=lesson,
        rendered_content=rendered_content,
        is_owner=is_entity_owner(EntityEnum.LESSON, lesson["lessonid"]),  # pyright: ignore
    )


@lesson_bp.route("/<int:id>/", methods=["GET", "POST"])
def update(id: int):
    ownership = is_entity_owner(EntityEnum.LESSON, id)
    if ownership is None:  # lesson doesn't exist
        return abort(404)
    elif not ownership:
        return abort(403)

    if request.method == "POST":
        form = request.form

        if not form["title"] or not form["content"]:
            return abort(400)

        db_execute(
            query="UPDATE lesson SET course = ?, title = ?, content = ? WHERE lessonid = ?",
            params=(form["course"], form["title"], form["content"], id),
            commit=True,
        )

        flash("Lesson updated.")
        return redirect(url_for(".view", id=id))

    lesson = db_execute(
        "SELECT * FROM lesson where lessonid = ?", params=(id,), fetch_type=1
    )
    return render_template(
        "editor.html",
        title="New Lesson",
        owned_courses=db_execute(
            query="SELECT * FROM course WHERE owner = ?",
            params=(g.get("user")["userid"],),
            fetch_type=3,
        ),
        courseid=lesson["course"],  # pyright: ignore
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
