from os import getenv
from secrets import token_hex

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base config"""

    DATABASE = "courses.db"
    RENDER_TAGS = [
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "p",
        "a",
        "b",
        "strong",
        "em",
        "ol",
        "ul",
        "li",
        "code",
        "blockquote",
        "img",
    ]
    RENDER_ATTRS = {"*": ["class"], "a": ["href"], "img": ["alt", "src"]}
    SECRET_KEY = getenv("SECRET_KEY", token_hex(16))
