from fastapi import Depends, FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import config
from app.database import engine, models
from app.dependencies import MEDIA_PATH, STATIC_PATH, get_db, logger, templates
from app.internal import daily_quotes, json_data_loader
from app.internal.languages import set_ui_language
from app.routers.salary import routes as salary


def create_tables(engine, psql_environment):
    if 'sqlite' in str(engine.url) and psql_environment:
        raise models.PSQLEnvironmentError(
            "You're trying to use PSQL features on SQLite env.\n"
            "Please set app.config.PSQL_ENVIRONMENT to False "
            "and run the app again."
        )
    else:
        models.Base.metadata.create_all(bind=engine)


create_tables(engine, config.PSQL_ENVIRONMENT)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")
app.logger = logger

# This MUST come before the app.routers imports.
set_ui_language()

from app.routers import (agenda, calendar, categories, celebrity,  # noqa: E402
                         currency, dayview, email, event, invitation, profile,
                         search, telegram, whatsapp)

json_data_loader.load_to_db(next(get_db()))

routers_to_include = [
    agenda.router,
    calendar.router,
    categories.router,
    celebrity.router,
    currency.router,
    dayview.router,
    email.router,
    event.router,
    invitation.router,
    profile.router,
    salary.router,
    search.router,
    telegram.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)


@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page for the website."""
    quote = daily_quotes.quote_per_day(db)
    user_quotes = daily_quotes.get_quotes(db, 1)
    for user_quote in user_quotes:
        if user_quote.id == quote.id:
            quote.is_favorite = True
    return templates.TemplateResponse("home.html", {
        "request": request,
        "quote": quote,
    })


@app.post("/")
async def save_or_delete_quote(
    user_id: int = Form(...),
    quote: str = Form(...),
    to_save: bool = Form(...),
        db: Session = Depends(get_db)):
    """Saves or deletes a quote from the database."""
    if to_save:
        daily_quotes.save_quote(db, user_id, quote)
    else:
        daily_quotes.remove_quote(db, user_id, quote)


@app.get("/favorite_quotes")
async def favorite_quotes(
    request: Request,
    db: Session = Depends(get_db),
        user_id: int = 1):
    """html page for displaying the users' favorite quotes."""
    quotes = daily_quotes.get_quotes(db, user_id)
    return templates.TemplateResponse("favorite_quotes.html", {
        "request": request,
        "quotes": quotes,
    })
