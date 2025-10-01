from flask import Flask

from .db import close_db, register_commands
from .views import register_blueprints


def create_app():
    app = Flask(__name__, template_folder="web/templates", static_folder="web/static")

    app.config.from_object("src.config.Config")

    register_blueprints(app)
    register_commands(app)

    app.teardown_appcontext(close_db)

    return app
