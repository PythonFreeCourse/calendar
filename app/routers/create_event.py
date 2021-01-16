from typing import Optional
from datetime import datetime
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))



from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel




app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="../templates")


@app.get("/profile/EditEvent", response_class=HTMLResponse)
async def insert_info(request: Request):
    return templates.TemplateResponse("editevent.html",{"request": request})


@app.post("/profile#id={user_id}/EditEvent")
def create_item(user_id: int, event_title: str = Form(...), location: Optional[str] = Form(None), from_date: Optional[datetime] = Form(...),
                to_date: Optional[datetime] = Form(...), link_vc: str = Form(None), content: str = Form(None), repeated_event: str = Form(None)):
    # requierd args - title, from_date, to_date, user_id
    # check validation for the return valuo 
    # if the prosess success return json with True boolean arg and the event_id
    # return False otherwith
    prosess = False
    event_valuo = {'title': event_title, "location": location, "from_date": from_date, "to_date": to_date, "link_vc":link_vc, "content": content, 
                    "repeated_event": repeated_event}
    # try:
    if check_validation(event_title, from_date, to_date):
        pass
        # x = Event.content
    # insert the valuo to the DB with SQLalcemy 

#  except Exception as identifier:
    # pass
    return {from_date < to_date}


def check_validation(title, start_time, end_time):
    if title is not None:
        if start_time < end_time:
            return True
    return False