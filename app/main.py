from fastapi import Depends, FastAPI, Request, status
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import app.internal.features as internal_features
from app import config
from app.database import engine, models
from app.dependencies import (
    MEDIA_PATH,
    SOUNDS_PATH,
    STATIC_PATH,
    UPLOAD_PATH,
    SessionLocal,
    get_db,
    logger,
    templates,
)
from app.internal import daily_quotes, json_data_loader
from app.internal.languages import set_ui_language
from app.internal.security.dependencies import current_user
from app.internal.security.ouath2 import auth_exception_handler
from app.routers.salary import routes as salary
from app.utils.extending_openapi import custom_openapi


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
app.mount(
    "/event_images",
    StaticFiles(directory=UPLOAD_PATH),
    name="event_images",
)
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
    favorite_quotes,
    features,
    four_o_four,
    friendview,
    google_connect,
    joke,
    login,
    logout,
    meds,
    notification,
    profile,
    register,
    reset_password,
    search,
    settings,
    telegram,
    todo_list,
    user,
    weekview,
    weight,
    whatsapp,
)

json_data_loader.load_to_database(next(get_db()))


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
    favorite_quotes.router,
    features.router,
    four_o_four.router,
    friendview.router,
    google_connect.router,
    joke.router,
    login.router,
    logout.router,
    meds.router,
    notification.router,
    profile.router,
    register.router,
    reset_password.router,
    salary.router,
    search.router,
    settings.router,
    telegram.router,
    todo_list.router,
    user.router,
    weekview.router,
    weight.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)


@app.on_event("startup")
async def startup_event():
    session = SessionLocal()
    internal_features.create_features_at_startup(session=session)
    session.close()


# TODO: I add the quote day to the home page
# until the relevant calendar view will be developed.
@app.get("/", include_in_schema=False)
@logger.catch()
async def home(
    request: Request,
    db: Session = Depends(get_db),
) -> templates.TemplateResponse:
    """Home page for the website."""
    user_id = False
    if "Authorization" in request.cookies:
        jwt = request.cookies["Authorization"]
        user = await current_user(request=request, db=db, jwt=jwt)
        user_id = user.user_id
    is_connected = bool(user_id)
    quote_of_day = daily_quotes.get_quote_of_day(db)
    quote = daily_quotes.is_quote_favorite(db, user_id, quote_of_day)
    if is_connected and quote:
        quote_of_day.is_favorite = True
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "is_connected": is_connected,
            "quote": quote_of_day,
            "empty_heart": daily_quotes.EMPTY_HEART_PATH,
            "full_heart": daily_quotes.FULL_HEART_PATH,
        },
    )


custom_openapi(app)
