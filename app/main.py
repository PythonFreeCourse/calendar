from fastapi import Depends, FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dependencies import STATIC_PATH, TEMPLATES_PATH, get_db

from app.database import models
from app.database.database import Base, SessionLocal, engine
from app.routers import edit

# from starlette.requests import Request



app = FastAPI()
app.include_router(edit.router)

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

templates = Jinja2Templates(directory=TEMPLATES_PATH)

models.Base.metadata.create_all(bind=engine)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcouming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcouming_events
    })