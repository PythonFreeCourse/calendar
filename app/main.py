from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.database import models
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import agenda, event, profile

from app.internal.logger_customizer import LoggerCustomizer


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

# Configure logger
config_path=Path(__file__).parent / 'internal'
config_path = config_path.absolute() / "logging_config.json"
logger = LoggerCustomizer.make_logger(config_path, 'logger')
app.logger = logger


app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)


@app.get("/")
@app.logger.catch()
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })
