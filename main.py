import glob
import json
import mimetypes
import os
import re
import unicodedata
from datetime import datetime, timedelta

import aiofiles
import jinja2
import tornado.ioloop
import tornado.web
from dotenv import load_dotenv
from tornado.web import HTTPError

load_dotenv()

# Simple in-memory cache (similar to Flask-Caching simple)
image_cache = {}  # filename -> (content, content_type, last_modified)
CACHE_TIMEOUT = 3600  # seconds


loader = jinja2.FileSystemLoader("templates")
env = jinja2.Environment(loader=loader)


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


def get_all_folders() -> dict[str, str]:
    folder_names = {}
    static_pictures_path = os.getenv("STATIC_PICTURES_PATH", "static/pictures")
    for folder in glob.glob(f"{static_pictures_path}/*"):
        if os.path.isdir(folder):
            folder_name = os.path.basename(folder)
            folder_slug = slugify(folder_name)
            folder_names[folder_slug] = folder_name
    return folder_names


def get_all_images() -> dict[str, list[str]]:
    pictures = {}
    valid_image_extensions = {".jpeg", ".jpg", ".png", ".JPEG", ".JPG", ".PNG"}
    folders = get_all_folders()
    static_pictures_path = os.getenv("STATIC_PICTURES_PATH", "static/pictures")

    for folder_slug, folder_name in folders.items():
        images = [
            filename.replace(f"{static_pictures_path}/", "")
            .replace("\\", "/")
            .replace("//", "/")
            for filename in glob.iglob(
                f"{static_pictures_path}/{folder_name}/**", recursive=True
            )
            if os.path.isfile(filename)
            and os.path.splitext(filename)[1] in valid_image_extensions
        ]
        if images:
            pictures[folder_slug] = images

    return pictures


class BaseHandler(tornado.web.RequestHandler):
    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        namespace["get_all_folders"] = get_all_folders
        namespace["get_all_images"] = get_all_images
        return namespace


class IndexHandler(BaseHandler):
    def get(self):
        template = env.get_template("index.html")
        rendered_template = template.render(
            folders=get_all_folders(),
            pictures=get_all_images(),
        )
        self.write(rendered_template)


class GoogleHandler(BaseHandler):
    def get(self):
        self.write("google-site-verification: google9d968a11b4bf61f7.html")


class CementHandler(BaseHandler):
    def get(self):
        template = env.get_template("cement_calculator.html")
        rendered_template = template.render()
        self.write(rendered_template)


class PaintHandler(BaseHandler):
    def get(self):
        template = env.get_template("paint_calculator.html")
        rendered_template = template.render()
        self.write(rendered_template)


class BitsHandler(BaseHandler):
    def get(self):
        template = env.get_template("bits_app.html")
        rendered_template = template.render()
        self.write(rendered_template)


class GetImagesHandler(tornado.web.RequestHandler):
    def get(self):
        # Use simple cache
        now = datetime.now()
        cached = image_cache.get("images")
        if cached and now - cached["time"] < timedelta(seconds=CACHE_TIMEOUT):
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(cached["data"]))
        else:
            data = get_all_images()
            image_cache["images"] = {"data": data, "time": now}
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(data))


class LoadImageHandler(BaseHandler):
    async def get(self, filename: str):
        if filename.startswith("/"):
            filename = filename[1:]
        static_pictures_path = os.getenv("STATIC_PICTURES_PATH", "static/pictures")
        file_path = os.path.abspath(os.path.join(static_pictures_path, filename))

        if not file_path.startswith(os.path.abspath(static_pictures_path)):
            raise HTTPError(403, "Access denied.")

        if not os.path.exists(file_path):
            raise HTTPError(404, f"File not found: {filename}")

        file_mtime = os.path.getmtime(file_path)
        cache_entry = image_cache.get(filename)

        if cache_entry and cache_entry[2] == file_mtime:
            content, content_type, _ = cache_entry
        else:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()
            content_type, _ = mimetypes.guess_type(file_path)
            if not content_type:
                content_type = "application/octet-stream"
            image_cache[filename] = (content, content_type, file_mtime)

        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", content_type)
        self.set_header("Content-Length", str(len(content)))
        self.set_header("Accept-Ranges", "bytes")
        self.set_header("Content-Range", f"bytes 0-{len(content)-1}/{len(content)}")
        self.set_header("Content-Disposition", f'inline; filename="{filename}"')
        self.set_header("Cache-Control", "public, max-age=86400")

        self.write(content)
        await self.flush()
        self.finish()


def make_app():
    return tornado.web.Application(
        [
            (r"/", IndexHandler),
            (r"/cementcalculator", CementHandler),
            (r"/cement", CementHandler),
            (r"/cc", CementHandler),
            (r"/paintcalculator", PaintHandler),
            (r"/paint", PaintHandler),
            (r"/pc", PaintHandler),
            (r"/bits", BitsHandler),
            (r"/bitsapp", BitsHandler),
            (r"/get_images", GetImagesHandler),
            (r"/load_image/(.*)", LoadImageHandler),
            (r"/google9d968a11b4bf61f7.html", GoogleHandler),
        ],
        template_path="templates",
        static_path="static",
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(os.getenv("PORT", 5058))
    tornado.ioloop.IOLoop.current().start()
