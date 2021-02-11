from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app import config
from app.database import engine, models
from app.dependencies import (get_db, logger, MEDIA_PATH,
                              STATIC_PATH, templates, SessionLocal)
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

from app.routers import (  # noqa: E402
    agenda, calendar, categories, celebrity, currency, dayview,
    email, event, invitation, profile, search, telegram, whatsapp,
    feature_panel
)

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
    feature_panel.router,
]

for router in routers_to_include:
    app.include_router(router)


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
        logger.error('Not a feature - Access is allowed.  Error: ' + str(e))
        return await call_next(request)

    if is_enabled:
        # in case the feature is enabled
        return await call_next(request)

    if 'referer' not in request.headers:
        # in case request come from straight from url line on browser
        return RedirectResponse(url=app.url_path_for('home'))

    # in case the feature is disabled
    return RedirectResponse(url=request.headers['referer'])


@app.on_event("startup")
async def startup_event():
    session = SessionLocal()
    feature_panel.create_features_at_startup(session=session)
    session.close()


# TODO: I add the quote day to the home page
# until the relavent calendar view will be developed.
@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)

    return templates.TemplateResponse("home.html", {
        "request": request,
        "quote": quote,
    })
