from flask import Blueprint, render_template

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
    return render_template("home.html")
