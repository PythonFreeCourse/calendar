from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

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
async def add_process_time_header(request: Request, call_next,
                                  ):

    route = str(request.url)
    route = route.replace(str(request.base_url), '')
    # resp = await call_next(request)
    # print(resp['type'])
    # resp['type'] = "http.response.start"
    # user = session.query(models.User).filter_by(id=1).first()

    # if feature_panel.is_feature_enabled(route=route, user_id=1):
        # response = await call_next(request)
        # return response
    return await call_next(request)


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
