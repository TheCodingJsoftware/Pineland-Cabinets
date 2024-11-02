import glob
import os.path
import re
import unicodedata

from flask import Flask, render_template
from flask_caching import Cache
from flask import jsonify

app = Flask(__name__)
cache = Cache(app, config={"CACHE_TYPE": "simple"})

user_count: int = 0
file_name: str = ""


@app.route("/")
def index():
    return render_template(
        "index.html", folders=get_all_folders(), pictures=get_all_images()
    )


@app.route("/cementcalculator")
def cement_calculator():
    return render_template("cement_calculator.html")


@app.route("/cement")
def cement():
    return render_template("cement_calculator.html")


@app.route("/cc")
def cc():
    return render_template("cement_calculator.html")


@app.route("/paintcalculator")
def paint_calculator():
    return render_template("paint_calculator.html")


@app.route("/paint")
def paint():
    return render_template("paint_calculator.html")


@app.route("/pc")
def pc():
    return render_template("paint_calculator.html")


@app.route("/bits")
def bits():
    return render_template("bits_app.html")


@app.route("/bitsapp")
def bits_app():
    return render_template("bits_app.html")


@app.route("/get_images")
@cache.cached(timeout=3600)
def get_images():
    pictures = get_all_images()  # This returns the dictionary with all images
    return jsonify(pictures)


def get_all_images() -> dict[str, list[str]]:
    pictures = {}
    valid_image_extensions = {".jpeg", ".jpg", ".png", ".JPEG", ".JPG", ".PNG"}

    # Iterate over folders returned by get_all_folders and only add folders with images
    folders = get_all_folders()
    for folder_slug, folder_name in folders.items():
        images = [
            filename.replace("static/", "").replace("\\", "/")
            for filename in glob.iglob(
                f"static/pictures/{folder_name}/**", recursive=True
            )
            if os.path.isfile(filename)
            and os.path.splitext(filename)[1] in valid_image_extensions
        ]

        if images:  # Only add non-empty folders
            pictures[folder_slug] = images

    return pictures


def get_all_folders() -> dict[str, str]:
    folder_names = {}

    # Only list folders in "static/pictures" directory
    for folder in glob.glob("static/pictures/*"):
        if os.path.isdir(folder):  # Check if it is a folder
            folder_name = os.path.basename(folder)
            folder_slug = slugify(folder_name)
            folder_names[folder_slug] = folder_name

    return folder_names


def slugify(value, allow_unicode=False):
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


# app.run(host="localhost", port=5000)
