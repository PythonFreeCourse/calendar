from datetime import datetime
from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.database.countries import countries
from app.database import models
from app.database.models import Country
from app.database.database import engine
from app.database.database import get_db, SessionLocal
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import agenda, event, profile, email
from geoip import geolite2
import pytz


models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(email.router)


def add_countries_to_db():
    """
    Adding all new countries to the "Country" table in the database.
    Information is based on the "countries" list.
    (The list is located in app/database/countries.py)
    Names are described either as:
    "Country Name, City Name" or
    "Country Name" solely.
    Timezones are described as "Continent/ City Name"
    for example:
        name: Israel, Jerusalem
        timezone: Asia/Jerusalem
    """
    session = SessionLocal()
    for country in countries:
        partial_name = country['name']
        for capital in country['timezones']:
            capital_name = capital.split('/')[-1]
            if partial_name != capital_name:
                name = partial_name + ', ' + capital_name
            else:
                name = capital_name
            existing = session.query(Country).filter_by(name=name).first()
            if not existing:
                new_country = Country(name=name, timezone=str(capital))
                session.add(new_country)
    session.commit()
    session.close()


add_countries_to_db()


@app.get("/")
async def home(
    request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/global_time")
async def time(
    request: Request):
    """
    Displays a globe icon.
    By Click the page transfers to "/global_time/choose".
    """
    return templates.TemplateResponse("event/partials/global_time.html", {
        "request": request
    })


@app.get("/global_time/choose")
async def time_choose(
        request: Request,
        session=Depends(get_db)):
    """
    Displays the list of all countries name from "Country" table.
    By Click on country name the page transfers to:
    "/global_time/{country_name}/{chosen_datetime}".
    *** Temporarily  returns a fictitious meeting datetime. ***
    """
    data = session.query(Country.name).all()
    temp_meeting_datetime = '2021-02-10 19:00:00'
    ip = request.client.host
    return templates.TemplateResponse("event/partials/global_time.html", {
        "request": request,
        "data": data,
        "date": temp_meeting_datetime,
        "ip": ip
    })


@app.get("/global_time/{country}/{datetime}/{ip}")
async def time_conv(
        ip,
        country,
        datetime: datetime,
        request: Request,
        session=Depends(get_db)):
    """
    Displays the chosen country name and the meeting time,
    converted to it's local time.
    If the Users IP is not recognized , displays error message
    """
    error_msg = """
    Your ip address is not associated with any geographical location.
    This function cannot operate.
    """
    match = geolite2.lookup(ip)
    if match is not None:
        ip_tmz = match.timezone
        target_tmz = session.query(Country.timezone).filter_by(name=country).first()
        target_tmz = target_tmz[0]
        meeting_time_with_utc = pytz.timezone(ip_tmz).localize(datetime)
        target_with_utc = pytz.timezone(target_tmz)
        target_time = meeting_time_with_utc.astimezone(target_with_utc)
        target_meeting_hour = target_time.strftime("%H:%M")
        return templates.TemplateResponse("event/partials/global_time.html", {
            "request": request,
            "time": target_meeting_hour,
            "country": country
        })
    else:
        return templates.TemplateResponse("event/partials/global_time.html", {
            "request": request,
            "msg": error_msg
        })
