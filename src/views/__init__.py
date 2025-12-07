from flask import Blueprint, g, render_template

from src.db import db_execute

from .auth import auth_bp
from .course import course_bp
from .lesson import lesson_bp

root_bp: Blueprint = Blueprint("root", __name__)
BLUEPRINTS = [lesson_bp, auth_bp, course_bp]


def register_blueprints(app):
    # register child blueprints under root
    for bp in BLUEPRINTS:
        root_bp.register_blueprint(bp)
    # register root and children under app
    app.register_blueprint(root_bp)


@root_bp.route("/")
def index():
    if g.get("user"):
        courses = db_execute(
            # select all courses that belong to current user and the number of lessons in each course
            query="SELECT course.*, count(lesson.lessonid) AS lessoncount FROM course LEFT JOIN lesson ON course.courseid = lesson.course WHERE course.owner = ? GROUP BY course.courseid;",
            params=(g.user["userid"],),
            fetch_type=3,
        )
        return render_template("home.html", courses=courses)

    return render_template("home.html")
