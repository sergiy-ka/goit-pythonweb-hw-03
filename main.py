from aiohttp import web
import aiofiles
import json
from datetime import datetime
import pathlib
from jinja2 import Environment, FileSystemLoader

# Шляхи та директорії
BASE_DIR = pathlib.Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
STORAGE_DIR = BASE_DIR / "storage"

STORAGE_DIR.mkdir(exist_ok=True)
DATA_FILE = STORAGE_DIR / "data.json"

# Jinja2
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


async def index(request):
    return web.FileResponse(TEMPLATES_DIR / "index.html")


async def message_page(request):
    return web.FileResponse(TEMPLATES_DIR / "message.html")


async def handle_message(request):
    data = await request.post()
    message_data = {"username": data["username"], "message": data["message"]}

    try:
        async with aiofiles.open(DATA_FILE, mode="r") as f:
            content = await f.read()
            messages = json.loads(content)
    except FileNotFoundError:
        messages = {}

    timestamp = str(datetime.now())
    messages[timestamp] = message_data

    async with aiofiles.open(DATA_FILE, mode="w") as f:
        await f.write(json.dumps(messages, indent=2))

    raise web.HTTPFound(location="/read")


async def read_messages(request):
    try:
        async with aiofiles.open(DATA_FILE, mode="r") as f:
            content = await f.read()
            messages = json.loads(content)
    except FileNotFoundError:
        messages = {}

    template = env.get_template("read.html")
    html = template.render(messages=messages)
    return web.Response(text=html, content_type="text/html")


async def handle_404(request):
    return web.FileResponse(TEMPLATES_DIR / "error.html", status=404)


app = web.Application()

# Маршрути
app.router.add_get("/", index)
app.router.add_get("/message.html", message_page)
app.router.add_post("/message", handle_message)
app.router.add_get("/read", read_messages)
app.router.add_static("/static", STATIC_DIR)
app.router.add_route("*", "/{tail:.*}", handle_404)

if __name__ == "__main__":
    port = 3000
    web.run_app(
        app, port=port, print=lambda s: print(f"Running on http://localhost:{port}")
    )
