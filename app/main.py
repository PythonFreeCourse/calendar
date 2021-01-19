from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import app


# app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

app.logger.debug("shimishinmiyeah")
app.logger.info("shimishinmiyeah")
app.logger.error("shimishinmiyeah")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcoming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcoming_events
    })


@app.get('/custom-logger')
def customize_logger(request: Request):
    request.app.logger.info("Here Is Your Info Log")
    try:
        a = 1 / 0
    except ZeroDivisionError:
        request.app.logger.error("Here Is Your Error Log")
    return {'data': "Successfully Implemented Custom Log"}
