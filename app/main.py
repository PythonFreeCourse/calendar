from os.path import relpath

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app import config
from app.database import engine, models
from app.dependencies import (
    get_db,
    logger,
    MEDIA_PATH,
    SOUNDS_PATH,
    STATIC_PATH,
    templates,
)
from app.internal import daily_quotes, json_data_loader
from app.internal.languages import set_ui_language
from app.internal.security.dependencies import current_user
from app.internal.security.ouath2 import auth_exception_handler
from app.routers.salary import routes as salary


def create_tables(engine, psql_environment):
    if "sqlite" in str(engine.url) and psql_environment:
        raise models.PSQLEnvironmentError(
            "You're trying to use PSQL features on SQLite env.\n"
            "Please set app.config.PSQL_ENVIRONMENT to False "
            "and run the app again.",
        )
    else:
        models.Base.metadata.create_all(bind=engine)


create_tables(engine, config.PSQL_ENVIRONMENT)

app = FastAPI(title="Pylander", docs_url=None)
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")
app.mount("/static/tracks", StaticFiles(directory=SOUNDS_PATH), name="sounds")
app.logger = logger

app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, auth_exception_handler)

# This MUST come before the app.routers imports.
set_ui_language()

from app.routers import (  # noqa: E402
    about_us,
    agenda,
    audio,
    calendar,
    categories,
    celebrity,
    credits,
    currency,
    dayview,
    email,
    event,
    export,
    four_o_four,
    friendview,
    google_connect,
    invitation,
    joke,
    login,
    logout,
    meds,
    profile,
    register,
    search,
    telegram,
    user,
    weekview,
    weight,
    whatsapp,
)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


routers_to_include = [
    about_us.router,
    agenda.router,
    audio.router,
    calendar.router,
    categories.router,
    celebrity.router,
    credits.router,
    currency.router,
    dayview.router,
    email.router,
    event.router,
    export.router,
    four_o_four.router,
    friendview.router,
    google_connect.router,
    invitation.router,
    joke.router,
    login.router,
    logout.router,
    meds.router,
    profile.router,
    register.router,
    salary.router,
    search.router,
    telegram.router,
    user.router,
    weekview.router,
    weight.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)

json_data_loader.load_to_database(next(get_db()))

EMPTY_HEART_PATH = relpath(f"{MEDIA_PATH}\\empty_heart.png", "app")
FULL_HEART_PATH = relpath(f"{MEDIA_PATH}\\full_heart.png", "app")


@app.get("/", include_in_schema=False)
@logger.catch()
async def home(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    """Home page for the website."""
    quote_of_day = daily_quotes.get_quote_of_day(db)
    if daily_quotes.is_quote_favorite(db, user.user_id, quote_of_day):
        quote_of_day.is_favorite = True
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "quote": quote_of_day,
            "empty_heart": EMPTY_HEART_PATH,
            "full_heart": FULL_HEART_PATH,
        },
    )


@app.post("/")
async def save_quote(
    user: models.User = Depends(current_user),
    quote_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Saves a quote in the database."""
    record = (
        db.query(models.UserQuotes)
        .filter(
            models.UserQuotes.user_id == user.user_id,
            models.UserQuotes.quote_id == quote_id,
        )
        .first()
    )
    if not record:
        db.add(models.UserQuotes(user_id=user.user_id, quote_id=quote_id))
        db.commit()


@app.delete("/")
async def delete_quote(
    user: models.User = Depends(current_user),
    quote_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Deletes a quote from the database."""
    db.query(models.UserQuotes).filter(
        models.UserQuotes.user_id == user.user_id,
        models.UserQuotes.quote_id == quote_id,
    ).delete()
    db.commit()


@app.get("/favorite_quotes")
async def favorite_quotes(
    request: Request,
    db: Session = Depends(get_db),
    user: models.User = Depends(current_user),
):
    """html page for displaying the users' favorite quotes."""
    quotes = daily_quotes.get_quotes(db, user.user_id)
    return templates.TemplateResponse(
        "favorite_quotes.html",
        {
            "request": request,
            "quotes": quotes,
            "full_heart": FULL_HEART_PATH,
        },
    )
