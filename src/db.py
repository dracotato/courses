import sqlite3
from os import path

import click
from flask import Flask, g
from flask import current_app as ca


# db
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(
            path.join(ca.instance_path, ca.config["DATABASE"]),
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")  # enable foreign keys

    return g.db


def close_db(_=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    with ca.open_resource("schema.sql", mode="r") as f:
        get_db().executescript(f.read())


# Commands
@click.command("init-db")
def init_db_cmd():
    """Create the db tables if they don't exist."""
    init_db()
    click.echo("Initialized the database.")


def register_commands(app: Flask):
    app.cli.add_command(init_db_cmd)
