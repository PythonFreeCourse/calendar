from typing import Optional


from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


# from app.database.models import * 

app = FastAPI()

# app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="../templates")


@app.get("/Calender/EditEvent", response_class=HTMLResponse)
async def insert_info(request: Request):
    return templates.TemplateResponse("editevent.html",{"request": request})


@app.post("/Calender/EditEvent")
def create_item(eventtitle: str = Form(...), location: Optional[str] = Form(None), from_date: str = Form(...), to_date: str = Form(...),
                 linkvc: str = Form(...), content: str = Form(...), repeatedevent: str = Form(...)):
    # requierd args - title, from_date, to_date, user_id
    # check validation for the return valuo 
    # insert the valuo to the DB with SQLalcemy 
    # if the prosess success return json with True boolean arg and the event_id
    # return False otherwith

    # print(eventtitle, location, from_date, to_date, linkvc, content, repeatedevent)
    return {to_date}
