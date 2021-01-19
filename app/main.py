from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database.database import Base, engine
from app.routers import email_send

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(email_send.router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


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
