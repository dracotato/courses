import sqlite3
from os import path
from typing import Any

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


def db_execute(
    query: str,
    params: tuple | dict | None = None,
    fetch_type=0,
    fetch_size=1,
    execute_many=False,
    commit=False,
    return_rowid=False,
) -> list[Any] | Any | None:
    """
    execute a query on the db and optionally return the result

    fetch:
        0 (default) — fetch nothing
        1 — equivalent to fetchone()
        2 — equivalent to fetchmany(), also set fetch_size
        3 — equivalent to fetchall()

    execute_many:
        execute the query once for each item in params

    commit:
        if set to true then also commit the transactions.

    return_rowid:
        return the rowid of the last created record.
        Note: discards fetch.
    """
    db = get_db()

    if params and execute_many:
        cur = db.executemany(query, params)
    elif params:
        cur = db.execute(query, params)
    else:
        cur = db.execute(query)

    result = None

    if return_rowid:
        result = cur.lastrowid

    elif fetch_type == 1:
        result = cur.fetchone()
    elif fetch_type == 2:
        result = cur.fetchmany(fetch_size)
    elif fetch_type == 3:
        result = cur.fetchall()

    cur.close()
    if commit:
        db.commit()

    return result


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
