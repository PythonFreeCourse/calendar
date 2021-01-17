from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import config
from .database import models
from .database.database import engine
from .routers import profile


models.Base.metadata.create_all(bind=engine)

MEDIA_PATH = Path(config.MEDIA_DIRECTORY).absolute()
STATIC_PATH = Path('app/static').absolute()

app = FastAPI()
app.include_router(profile.router)

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")


templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })
