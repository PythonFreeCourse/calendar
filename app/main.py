from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles

from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine, get_db
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import (agenda, currency, dayview, email, event, invitation, profile,
                         search)

from datetime import datetime
from sqlalchemy.orm import Session


models.Base.metadata.drop_all(bind=engine)
def create_tables(engine, psql_environment):
    if 'sqlite' in str(engine.url) and psql_environment:
        raise models.PSQLEnvironmentError(
            "You're trying to use PSQL features on SQLite env.\n"
            "Please set app.config.PSQL_ENVIRONMENT to False "
            "and run the app again."
        )
    else:
        models.Base.metadata.create_all(bind=engine)


create_tables(engine, PSQL_ENVIRONMENT)
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")


app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(dayview.router)
app.include_router(email.router)
app.include_router(invitation.router)
app.include_router(search.router)
app.include_router(currency.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
