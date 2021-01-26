from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.database import models
from app.database.database import engine
from app.dependencies import MEDIA_PATH, STATIC_PATH, templates
from app.internal.languages import setup_ui_language

# This MUST come before the app.routers import.
setup_ui_language()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

from app.routers import agenda, email, event, profile  # noqa: E402

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(email.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
    })
