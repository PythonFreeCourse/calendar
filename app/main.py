import uvicorn
import datetime
from event import Event
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")



@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/dayview")
def dayview(request: Request):
    start = datetime.datetime(year=2021, month=1, day=27, hour=7, minute=13)
    end = datetime.datetime(year=2021, month=1, day=27, hour=8, minute=42)
    event1 = Event(id=1, color='#FFDE4D', content='do nothing', start_date_n_time=start, end_date_n_time=end)
    start = datetime.datetime(year=2021, month=1, day=27, hour=9, minute=13)
    end = datetime.datetime(year=2021, month=1, day=27, hour=11, minute=55)
    event2 = Event(id=2, color='#EF5454', content='this line is too long for this shit and i keep on writing until there will be no more spaceeeee', start_date_n_time=start, end_date_n_time=end)
    events = [event1, event2]
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events,
        "MONTH": start.strftime("%B").upper(),
        "DAY": start.day
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

if __name__ == "__main__":
    uvicorn.run('main', host="0.0.0.0", port=8000, reload=True)