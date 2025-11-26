from flask import Blueprint, abort, g, json, redirect, render_template, request, url_for

from src.db import db_execute
from src.utils import EntityEnum, delete_entity, is_entity_owner, join_web
from src.views.auth import check_login

course_bp: Blueprint = Blueprint(
    "course",
    __name__,
    url_prefix="/course",
    template_folder=join_web("templates/course"),
)

course_bp.before_request(check_login)


@course_bp.route("/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        course_id = db_execute(
            query="INSERT INTO course (title, desc, owner) VALUES (?,?,?)",
            params=(
                request.form["title"],
                request.form["desc"],
                g.get("user")["userid"],
            ),
            commit=True,
            return_rowid=True,
        )

        return redirect(url_for(".view", id=course_id))
    else:
        return render_template("form.html", title="New Course")


@course_bp.route("/v/<int:id>/")
def view(id: int):
    course = db_execute(
        query="SELECT * FROM course WHERE courseid = ?", params=(id,), fetch_type=1
    )

    if not course:
        abort(404)

    return render_template(
        "view.html",
        title="View Course",
        course_title=course["title"],  # pyright: ignore
        course_desc=course["desc"],  # pyright: ignore
        course_id=id,  # pyright: ignore
        is_owner=is_entity_owner(EntityEnum.COURSE, id),  # pyright: ignore
        owner_username=g.get("user")["username"],
        lessons=db_execute(
            query="SELECT * FROM lesson WHERE course = ?", params=(id,), fetch_type=3
        ),
    )


@course_bp.route("/<int:id>/", methods=["GET", "POST"])
def update(id: int):
    ownership = is_entity_owner(EntityEnum.COURSE, id)
    if ownership is None:  # course doesn't exist
        return abort(404)
    elif not ownership:
        return abort(403)

    course = db_execute(
        "SELECT * FROM course where courseid = ?", params=(id,), fetch_type=1
    )

    if request.method == "POST":
        db_execute(
            query="UPDATE course SET title = ?, desc = ? WHERE courseid = ?",
            params=(request.form["title"], request.form["desc"], id),
            commit=True,
        )

        return redirect(url_for(".view", id=id))
    else:
        return render_template(
            "form.html",
            title="New Course",
            course_title=course["title"],  # pyright: ignore
            course_desc=course["desc"],  # pyright: ignore
        )


@course_bp.route("/", methods=["DELETE"])
def delete():
    body = request.json
    response = {}

    # one course
    if isinstance(body, int):
        response[str(body)] = delete_entity(EntityEnum.COURSE, body)
    # many courses
    elif isinstance(body, list) and all([isinstance(x, int) for x in body]):
        for id in body:
            response[str(id)] = delete_entity(EntityEnum.COURSE, id)
    else:
        abort(400)  # bad request

    return json.jsonify(response)
