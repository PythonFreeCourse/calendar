from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import models
from app.database.database import engine, get_db
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.internal.quotes import load_quotes, daily_quotes
from app.routers import agenda, dayview, event, profile, email, invitation


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

load_quotes.load_daily_quotes(next(get_db()))

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(dayview.router)
app.include_router(email.router)
app.include_router(invitation.router)


# TODO: I add the quote day to the home page
# until the relavent calendar view will be developed.
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
        "quote": quote
    })
