import contextlib
import glob
import json
import os.path
import re
import time
import unicodedata
from ast import Index
from datetime import datetime

# import dropbox
from natsort import natsorted
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from flask import Flask, render_template

app = Flask(__name__)

user_count: int = 0
file_name: str = ""

@app.route("/")
def index() -> None:
    # global user_count, file_name
    # file_name = (
    #     "static/graphs/"
    #     + datetime.now().strftime("%B %d %A %Y")
    #     + ".json"
    # )
    # check_user_log_file()
    # json_data = get_user_count_data()
    # user_count += 1
    # json_data[len(list(json_data.keys()))] = {
    #     "date": datetime.now().strftime("%I:%M:%S %p"),
    #     "count": user_count,
    # }
    # with open(file_name, "w", encoding="utf-8") as f:
    #     json.dump(json_data, f)
    # remove_user_count()
    # archive()
    return render_template(
        "index.html", folders=get_all_folders(), pictures=get_all_images()
    )


@app.route("/user_count.html")
def graphs():
    return render_template("user_count.html", first_graph=get_first_graph(), graphs=get_all_user_graphs())


@app.route("/cementcalculator")
def cement_calculator():
    return render_template("cement_calculator.html")

@app.route("/cement")
def cement():
    return render_template("cement_calculator.html")

@app.route("/cc")
def cc():
    return render_template("cement_calculator.html")

@app.route("/bits")
def bits():
    return render_template("bits_app.html")

@app.route("/bitsapp")
def bits_app():
    return render_template("bits_app.html")


def check_user_log_file() -> None:
    if not os.path.isfile(file_name):
        with open(file_name, "w", encoding="utf-8") as f:
            line = (
                '{"0":{"date": "'
                + datetime.now().strftime("%I:%M:%S %p")
                + '", "count": 0}}'
            )
            f.write(line)


def get_user_count_data() -> dict:
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def archive() -> None:
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

    ax.plot(
        dates,
        values,
        color=(25 / 255, 203 / 255, 202 / 255),
        label=datetime.now().strftime("%B %d %A %Y"),
    )
    ax.set_xlim([0, len(dates)])
    ax.set_xticklabels(dates, rotation=45, ha="right")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(30))
    ax.xaxis.set_minor_locator(mticker.MaxNLocator(1))

    @mticker.FuncFormatter
    def major_formatter(x, pos):
        try:
            return dates[int(x)]
        except IndexError:
            return dates[-1]

    ax.xaxis.set_major_formatter(major_formatter)
    plt.legend()
    fig.savefig(file_name.replace(".json", ".png"), dpi=300)


def get_all_user_graphs() -> dict:
    pictures = []
    graphs_found: int = 0
    with contextlib.suppress(IndexError):
        search_dir = "static/graphs/"
        files = list(filter(os.path.isfile, glob.glob(search_dir + "*.png")))
        files.sort(key=lambda x: os.path.getmtime(x))
        files.reverse()
        for filename in files[1:]:
            filename = filename.replace("\\", "/")
            if "." in filename and filename.endswith(".png"):
                pictures.append(filename)
                graphs_found += 1
    picture_names = {}
    for picture in pictures:
        name = picture.replace('static/graphs/','').replace('.png','')
        picture_names[name] = picture
    return picture_names

def get_first_graph() -> dict:
    pictures = []
    with contextlib.suppress(IndexError):
        search_dir = "static/graphs/"
        files = list(filter(os.path.isfile, glob.glob(search_dir + "*.png")))
        files.sort(key=lambda x: os.path.getmtime(x))
        files.reverse()
        filename = files[0].replace("\\", "/")
        if "." in filename and filename.endswith(".png"):
            pictures.append(filename)
    picture_names = {}
    for picture in pictures:
        name = picture.replace('static/graphs/','').replace('.png','')
        picture_names[name] = picture
    return picture_names



def get_all_images() -> dict:
    pictures = {"All": []}
    for folder in list(get_all_folders().keys()):
        pictures[folder] = []
    with contextlib.suppress(IndexError):
        for filename in glob.iglob(
            "static/pictures" + "**/**",
            recursive=True,
        ):
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
    # with open("/volume1/web/pineland-cabinets-master/static/pictures/uploaded_list.json", "r") as f:
    #     json_data = json.load(f)
    #     for folder in list(json_data.keys()):
    #         for file in json_data[folder]:
    #             pictures["All"].append(json_data[folder][file])
    #             pictures[slugify(folder)].append(json_data[folder][file])
    return pictures


def get_all_folders() -> dict:
    folder_names = {"All": "All"}
    with contextlib.suppress(IndexError):
        for filename in glob.iglob(
            "static/pictures" + "**/**",
            recursive=False,
        ):
            filename = filename.replace("\\", "/")
            folder_names[
                slugify(filename.split("/")[-1]).replace("staticpictures", "")
            ] = (
                filename.split("/")[-1].replace("static/", "").replace("pictures/", "")
            )
    # with open("/volume1/web/pineland-cabinets-master/static/pictures/uploaded_list.json", "r") as f:
    #     json_data = json.load(f)
    #     for folder in list(json_data.keys()):
    #         folder_names[slugify(folder)] = folder
    return folder_names


def remove_user_count() -> None:
    global user_count
    time.sleep(60 * 5)  # 5 minutes
    user_count -= 1

    json_data = get_user_count_data()

    json_data[len(list(json_data.keys()))] = {
        "date": datetime.now().strftime("%I:%M:%S %p"),
        "count": user_count,
    }
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(json_data, f)
    archive()


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


app.run(host="10.10.80.93", port=5000)
