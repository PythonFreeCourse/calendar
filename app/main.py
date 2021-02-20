from fastapi import Depends, FastAPI, Form, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED

from app import config
from app.database import engine, models
from app.database.models import UserQuotes
from app.dependencies import (
    MEDIA_PATH,
    STATIC_PATH,
    get_db,
    logger,
    templates,
)
from app.internal import daily_quotes, json_data_loader
from app.internal.daily_quotes import get_quote_id
from app.internal.languages import set_ui_language
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
app.logger = logger

app.add_exception_handler(HTTP_401_UNAUTHORIZED, auth_exception_handler)

json_data_loader.load_to_db(next(get_db()))
# This MUST come before the app.routers imports.
set_ui_language()

from app.routers import (  # noqa: E402
    about_us,
    agenda,
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
    login,
    logout,
    profile,
    register,
    search,
    telegram,
    user,
    weekview,
    whatsapp,
)

json_data_loader.load_to_db(next(get_db()))


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
    calendar.router,
    categories.router,
    celebrity.router,
    credits.router,
    currency.router,
    dayview.router,
    friendview.router,
    weekview.router,
    email.router,
    event.router,
    export.router,
    four_o_four.router,
    google_connect.router,
    invitation.router,
    login.router,
    logout.router,
    profile.router,
    register.router,
    salary.router,
    search.router,
    telegram.router,
    user.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)

EMPTY_HEART_PATH = "media/empty_heart.png"
FULL_HEART_PATH = "media/full_heart.png"


@app.get("/", include_in_schema=False)
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page for the website."""
    quote = daily_quotes.quote_per_day(db)
    user_quotes = daily_quotes.get_quotes(db, 1)
    print(quote.id)
    print(quote.text)
    print(quote.is_favorite)
    for user_quote in user_quotes:
        if user_quote.id == quote.id:
            quote.is_favorite = True
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "quote": quote,
            "empty_heart": EMPTY_HEART_PATH,
            "full_heart": FULL_HEART_PATH,
        },
    )


@app.post("/")
async def save_quote(
    user_id: int = Form(...),
    quote: str = Form(...),
    db: Session = Depends(get_db),
):
    """Saves a quote in the database."""
    quote_id = get_quote_id(db, quote)
    record = (
        db.query(UserQuotes)
        .filter(UserQuotes.user_id == user_id, UserQuotes.quote_id == quote_id)
        .first()
    )
    if not record:
        db.add(UserQuotes(user_id=user_id, quote_id=quote_id))
        db.commit()


@app.delete("/")
async def delete_quote(
    user_id: int = Form(...),
    quote: str = Form(...),
    db: Session = Depends(get_db),
):
    """Deletes a quote from the database."""
    quote_id = get_quote_id(db, quote)
    db.query(UserQuotes).filter(
        UserQuotes.user_id == user_id,
        UserQuotes.quote_id == quote_id,
    ).delete()
    db.commit()


@app.get("/favorite_quotes")
async def favorite_quotes(
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = 1,
):
    """html page for displaying the users' favorite quotes."""
    quotes = daily_quotes.get_quotes(db, user_id)
    return templates.TemplateResponse(
        "favorite_quotes.html",
        {
            "request": request,
            "quotes": quotes,
            "full_heart": FULL_HEART_PATH,
        },
    )
