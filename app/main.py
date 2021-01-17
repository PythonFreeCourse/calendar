import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import routers.calendar_grid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


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


@app.get("/monthview")
async def monthview(request: Request):
    date = datetime.date.today()
    return templates.TemplateResponse("monthview.html", {
        "request": request,
        "calendar": {
            'date': date,
            'strf_date': routers.calendar_grid.get_date_as_string(date),
            'days_of_the_week': routers.calendar_grid.DAYS_OF_THE_WEEK,
            'month_block': routers.calendar_grid.get_month_block(
                datetime.date(date.year, date.month, 1)
            )
        }})


if __name__ == "__main__":
    uvicorn.run(app)
