from flask import Flask, g, current_app as ca
from os import path
import sqlite3
import click


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            path.join(ca.instance_path, ca.config["DATABASE"]),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    res = cur.fetchall()
    cur.close()

    return (res[0] if res else None) if one else res


def init_db():
    cur = get_db().cursor()

    with ca.open_resource("schema.sql", mode="r") as f:
        cur.executescript(f.read())


# Commands
@click.command("init-db")
def init_db_cmd():
    """Create the db tables if they don't exist."""
    init_db()
    click.echo("Initialized the database.")


def register_commands(app: Flask):
    app.cli.add_command(init_db_cmd)
