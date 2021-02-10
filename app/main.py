from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine, get_db
from app.dependencies import (logger, MEDIA_PATH, STATIC_PATH, templates)
from app.internal import daily_quotes, json_data_loader
from app.routers import (
    agenda, calendar, categories, dayview, email,
    event, invitation, profile, search, telegram, whatsapp, feature_panel
)
from app.telegram.bot import telegram_bot


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

json_data_loader.load_to_db(next(get_db()))

app.logger = logger

routers_to_include = [
    agenda.router,
    calendar.router,
    categories.router,
    dayview.router,
    email.router,
    event.router,
    invitation.router,
    profile.router,
    search.router,
    telegram.router,
    whatsapp.router,
    feature_panel.router,
]

for router in routers_to_include:
    app.include_router(router)

telegram_bot.set_webhook()


@app.middleware("http")
async def filter_access_to_features(request: Request, call_next):

    # getting the url route path for matching with the database
    route = str(request.url).replace(str(request.base_url), '')[:-1]

    try:
        is_enabled = feature_panel.is_feature_enabled(route=route)
        # session.close()
    except AttributeError as e:
        '''
        in case there is no feature exist in
        the database that match the route that passed to the request.
        '''
        logger.error(e)
        logger.warning('Not a feature - Access is allowed.')
        return await call_next(request)

    if is_enabled:
        # in case the feature is enabled
        return await call_next(request)

    if 'referer' not in request.headers:
        # in case request come from straight from url line on browser
        return RedirectResponse(url=app.url_path_for('home'))

    # in case the feature is disabled
    return RedirectResponse(url=request.headers['referer'])


# TODO: I add the quote day to the home page
# until the relavent calendar view will be developed.
@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    print(app)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
        "quote": quote
    })
