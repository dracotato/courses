from flask import Blueprint, Flask

from .auth import auth_bp
from .lesson import lesson_bp

root_bp: Blueprint = Blueprint("root", __name__)
BLUEPRINTS = [root_bp, lesson_bp, auth_bp]


def register_blueprints(app: Flask):
    for bp in BLUEPRINTS:
        app.register_blueprint(bp)


@root_bp.route("/")
def index():
    return "Welcome Home!"
