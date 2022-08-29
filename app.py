import contextlib
import glob
import json
import os.path
import re
import threading
import time
import unicodedata
from ast import Index
from datetime import datetime

# import matplotlib.pyplot as plt
# import matplotlib.ticker as mticker
# import numpy as np
from flask import Flask, render_template

# from scipy.interpolate import make_interp_spline

app = Flask(__name__)

user_count: int = 0
file_name: str = ""


@app.route("/")
def index() -> None:
    global user_count, file_name
    """
    The function `index()` returns the rendered template `index.html`

    The function `index()` is a function that returns the rendered template `index.html`

    Returns:
      The index.html file
    """
    file_name = "static/graphs/" + datetime.now().strftime("%B %d %A %Y") + ".json"
    # check_user_log_file()
    # json_data = get_user_count_data()
    # user_count += 1
    # json_data[len(list(json_data.keys()))] = {
        # "date": datetime.now().strftime("%I:%M:%S %p"),
        # "count": user_count,
    # }
    # with open(file_name, "w") as f:
    #    json.dump(json_data, f)
    # threading.Thread(target=remove_user_count).start()
    # threading.Thread(target=archive).start()
    return render_template(
        "index.html", folders=get_all_folders(), pictures=get_all_images()
    )


@app.route("/user_count.html")
def graphs():
    return render_template("user_count.html", graphs=get_all_user_graphs())


def check_user_log_file() -> None:
    """
    If the file doesn't exist, create it and write a line to it
    """
    if not os.path.isfile(file_name):
        with open(file_name, "w") as f:
            line = (
                '{"0":{"date": "'
                + datetime.now().strftime("%I:%M:%S %p")
                + '", "count": 0}}'
            )
            f.write(line)


def get_user_count_data() -> dict:
    """
    It opens the file, reads the data, and returns the data as a dictionary

    Returns:
      A dictionary
    """
    with open(file_name, "r") as f:
        return json.load(f)


def archive() -> None:
    """
    It takes a JSON file, reads the data, and plots it on a graph

    Returns:
      The dates list is being returned.
    """
    fig, ax = plt.subplots(1, 1)
    plt.grid(axis="y", color="0.5")
    plt.grid(axis="x", color="0.5")
    fig.subplots_adjust(bottom=0.2)
    json_data = get_user_count_data()

    values = []
    dates = []
    indexes = []
    for i, _ in enumerate(json_data):
        date = json_data[str(i)]["date"]
        dates.append(date)
        values.append(int(json_data[str(i)]["count"]))
        indexes.append(i)

        # Smooth interpretation of data
    indexes = np.array(indexes)
    try:
        smooth = make_interp_spline(indexes, values)
    except ValueError:
        return

    smooth_x = np.linspace(indexes.min(), indexes.max(), 500)
    smooth_y = smooth(smooth_x)

    ax.plot(
        smooth_x,
        smooth_y,
        color=(25 / 255, 203 / 255, 202 / 255),
        alpha=1,
        label=datetime.now().strftime("%B %d %A %Y"),
    )

    # ax.plot(
    #     dates, values, color=listeners_count[host]["color"], label=title
    # )
    ax.set_xlim([0, len(dates)])
    ax.set_xticklabels(dates, rotation=45, ha="right")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(30))
    ax.xaxis.set_minor_locator(mticker.MaxNLocator(1))

    @mticker.FuncFormatter
    def major_formatter(x, pos):
        """
        It returns the dates in the dates list.
        Args:
            x: The x coordinate of the tick
            pos: the position of the tick
        Returns:
            The dates list is being returned.
        """
        try:
            return dates[int(x)]
        except IndexError:
            return dates[-1]

    ax.xaxis.set_major_formatter(major_formatter)
    plt.legend()
    fig.savefig(file_name.replace(".json", ".png"))


def get_all_user_graphs() -> dict:
    """
    It returns a dictionary of all the graphs in the static/graphs folder, with the keys being the
    filepaths and the values being a dictionary with the keys "L", "R", and "index". The value of "L" is
    a boolean that is True if there is a graph to the left of the current graph, and the value of "R" is
    a boolean that is True if there is a graph to the right of the current graph. The value of "index"
    is the index of the graph in the list of all graphs

    Returns:
      A dictionary of dictionaries.
    """
    pictures = {}
    graphs_found: int = 0
    with contextlib.suppress(IndexError):
        for filename in glob.iglob("static/graphs" + "**/**", recursive=True):
            filename = filename.replace("\\", "/")
            if "." in filename and filename.endswith(".png"):
                pictures[filename] = (
                    {"L": False, "R": True, "index": graphs_found}
                    if graphs_found == 0
                    else {"L": True, "R": True, "index": graphs_found}
                )

                graphs_found += 1
    last_picture = list(pictures.keys())[-1]
    pictures[last_picture] = {"L": True, "R": False}
    return pictures


def get_all_images() -> dict:
    """
    It takes all the images in the static/pictures folder and puts them into a dictionary with the
    folder name as the key and the image path as the value

    Returns:
      A dictionary of lists.
    """
    pictures = {"All": []}
    for folder in list(get_all_folders().keys()):
        pictures[folder] = []
    with contextlib.suppress(IndexError):
        for filename in glob.iglob("static/pictures" + "**/**", recursive=True):
            filename = filename.replace("\\", "/")
            if "." in filename and (
                filename.endswith(".JPEG")
                or filename.endswith(".JPG")
                or filename.endswith(".jpeg")
                or filename.endswith(".jpg")
                or filename.endswith(".PNG")
                or filename.endswith(".png")
            ):
                folder_name = slugify(filename.split("/")[-2]).replace(
                    "staticpictures", ""
                )
                pictures["All"].append(filename)
                pictures[folder_name].append(filename)
    return pictures


def get_all_folders() -> dict:
    """
    It returns a dictionary of all the folders in the pictures directory

    Returns:
      A dictionary of all the folders in the pictures directory.
    """
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


def remove_user_count() -> None:
    """
    It removes a user from the user count after 5 minutes
    """
    global user_count
    time.sleep(60 * 5)  # 5 minutes
    user_count -= 1

    json_data = get_user_count_data()

    json_data[len(list(json_data.keys()))] = {
        "date": datetime.now().strftime("%B %d %A %Y %I-%M-%S %p"),
        "count": user_count,
    }
    with open(file_name, "w") as f:
        json.dump(json_data, f)


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


# app.run(host="10.0.1.217", port=5000, debug=False, threaded=True)
