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
