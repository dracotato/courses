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
            form.get("course")
            and form.get("title")
            and form.get("content")
            and db_execute(
                query="SELECT * FROM course WHERE courseid = ? AND owner = ?",
                params=(form.get("course"), g.get("user")["userid"]),
                fetch_type=1,
            )
        ):
            lesson_order: int = (
                db_execute(
                    query="SELECT COUNT(*) as count FROM lesson WHERE course = ?",
                    params=(form.get("course"),),
                    fetch_type=1,
                )["count"]  # pyright: ignore
                + 1
            )
            db_execute(
                query="INSERT INTO lesson (title, content, ord, owner, course) VALUES (?,?,?,?,?)",
                params=(
                    form.get("title").strip(),
                    form.get("content").strip(),
                    lesson_order,
                    g.get("user")["userid"],
                    form.get("course"),
                ),
                commit=True,
                return_rowid=True,
            )
            flash("Lesson created.")
            if form.get("batch") == "0":
                return redirect(url_for("root.course.view", id=form.get("course")))
        else:
            flash(
                "Please fill all fields, and make sure you have the right permissions."
            )

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
        # if the user still hasn't been redirected, it means they're batch writing
        courseid=request.args.get("course") or form.get("course"),
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

        if not form.get("title") or not form.get("content"):
            return abort(400)

        db_execute(
            query="UPDATE lesson SET course = ?, title = ?, content = ? WHERE lessonid = ?",
            params=(form.get("course"), form.get("title"), form.get("content"), id),
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
