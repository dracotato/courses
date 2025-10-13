from os import getcwd, path


def join_web(sub_path: str):
    return path.join(getcwd(), "src/web", sub_path)
