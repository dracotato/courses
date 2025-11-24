from enum import Enum
from os import getcwd, path

from flask import g

from .db import db_execute


class EntityEnum(Enum):
    COURSE = "course"
    LESSON = "lesson"


def join_web(sub_path: str):
    return path.join(getcwd(), "src/web", sub_path)


def is_entity_owner(entity: EntityEnum, entity_id: int, return_entity=False):
    """check if logged in user owns an entity and return True, or False (doesn't belong to the user), or None (if it doesn't exist)

    if return_entity is set to True, then return entity instead of True
    """
    if not g.get("user"):
        return False

    db_entity = db_execute(
        # this is gonna break horribly if the schema changes even a little
        query=f"SELECT * FROM {entity.value} WHERE {entity.value}id = ?",
        params=(entity_id,),
        fetch_type=1,
    )

    if not db_entity:
        return
    elif db_entity["owner"] == g.get("user")["userid"]:  # pyright: ignore
        if return_entity:
            return db_entity
        else:
            return True
    else:
        return False


def delete_entity(entity: EntityEnum, entity_id: int):
    ownership = is_entity_owner(entity=entity, entity_id=entity_id)
    if ownership is None:
        return 404  # status code
    elif not ownership:
        return 403

    db_execute(
        query=f"DELETE FROM {entity.value} WHERE {entity.value}id = ?",
        params=(entity_id,),
        commit=True,
    )
    return 200
