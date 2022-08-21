import contextlib
import glob
import re
import unicodedata
from ast import Index

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index() -> None:
    """
    The function `index()` returns the rendered template `index.html`

    The function `index()` is a function that returns the rendered template `index.html`

    Returns:
      The index.html file
    """
    return render_template(
        "index.html", folders=get_all_folders(), pictures=get_all_images()
    )


def get_all_images() -> dict:
    pictures = {"All": []}
    for folder in list(get_all_folders().keys()):
        pictures[folder] = []
    with contextlib.suppress(IndexError):
        for filename in glob.iglob("static/pictures" + "**/**", recursive=True):
            filename = filename.replace("\\", "/")
            if "." in filename:
                folder_name = slugify(filename.split("/")[-2]).replace(
                    "staticpictures", ""
                )
                pictures["All"].append(filename)
                pictures[folder_name].append(filename)
    return pictures


def get_all_folders() -> dict:
    folder_names = {"All": "All"}
    with contextlib.suppress(IndexError):
        for filename in glob.iglob("static/pictures" + "**/**", recursive=False):
            filename = filename.replace("\\", "/")
            folder_names[
                slugify(filename.split("/")[-1]).replace("staticpictures", "")
            ] = (
                filename.split("/")[-1].replace("static/", "").replace("pictures/", "")
            )
    return folder_names


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


# app.run(host="10.0.0.217", port=5000, debug=False, threaded=True)
