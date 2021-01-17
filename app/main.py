import uvicorn
import datetime

from app.event import Event
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
templates = Jinja2Templates(directory="templates")
try:
    app.mount("/app/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
    templates = Jinja2Templates(directory="app/templates")




@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/dayview")
def dayview(request: Request):
    event_id = 123
    color = 'red'
    content = 'nothing'
    start = "03/2/2021 4:05"
    end = "03/2/2021 4:20"
    events = [Event(id=event_id, color=color,
                  content=content,start_datetime=start,
                  end_datetime=end)]
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events,
        "MONTH": events[0].start_time.strftime("%B").upper(),
        "DAY": events[0].start_time.day
        })'''
    
@app.post("/dayview")
async def dayview(request: Request):
    form = await request.json()
    events = [Event(**event) for event in form['events']]
    return templates.TemplateResponse("dayview.html", {
        "request": request,
        "events": events,
        "MONTH": events[0].start_time.strftime("%B").upper(),
        "DAY": form['day']
        })
'''

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
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)
