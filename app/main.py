from typing import Optional
from datetime import datetime


from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import models
from app.database.models import Event
from app.database.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)



def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app = FastAPI()

# app.mount("static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse('home.html',{
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


@app.get("/profile/{user_id}/EditEvent", response_class=HTMLResponse)
async def insert_info(request: Request):
    """Get request and return an html File"""
    return templates.TemplateResponse("editevent.html",{"request": request})


@app.post("/profile/{user_id}/EditEvent")
def create_item(user_id: int, event_title: str = Form(...), location: Optional[str] = Form(None), from_date: Optional[datetime] = Form(...),
                to_date: Optional[datetime] = Form(...), link_vc: str = Form(None), content: str = Form(None), repeated_event: str = Form(None),
                db = Depends(get_db)):
    """ required args - title, from_date, to_date, user_id, the 'from_date' need to be early from the 'to_date'.
    check validation for the value, insert the new data to DB 
    if the prosess success return True arg the event_id, otherwith return False and the error Type """
    success = False
    error_msg = ""
    event_value = {'title': event_title, "location": location, "from_date": from_date, "to_date": to_date, "link_vc":link_vc, "content": content, 
                    "repeated_event": repeated_event}
    if event_title is None:
        event_title = "No Title"
    try:
        if check_validation(from_date, to_date):
            new_event = add_event(event_value, user_id, db)
            success = True
            event_id = new_event.id
            error_msg = ""
        else:
            error_msg = "Error, Your date is invalid"
    except Exception as e:
        error_msg = e
    finally:
        if not success:
            event_id = None
        return {success, event_id, error_msg}


def check_validation(start_time, end_time):
    """Check if the start_date is smaller then the end_time"""
    if start_time < end_time:
        return True
    return False


def add_event(values: dict, user_id: int, db):
    """Get User values, User_id and the DB Session insert the values to the DB and refresh it
    return the Event Class item"""
    new_event = Event(title = values['title'],
                    start_date = values['from_date'],
                    end_date = values['to_date'],
                    VC_link = values['link_vc'],
                    content = values['content'],
                    location = values['location'],
                    owner_id = user_id
                    )
    db.add(new_event)   
    db.commit()
    db.refresh(new_event)
    return new_event    