import os

from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles

from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine
from app.dependencies import MEDIA_PATH, STATIC_PATH, templates
from app.routers import agenda, event, profile, search


if 'sqlite' in str(engine.url) and PSQL_ENVIRONMENT:
    raise models.PSQLEnvironmentError(
        "You're trying to use PSQL features on SQLite env.\n"
        "Please set app.config.PSQL_ENVIRONMENT to False and run the app again."
    )
else:
    models.Base.metadata.create_all(bind=engine)
    

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(search.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })
