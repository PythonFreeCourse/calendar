from app.config import PSQL_ENVIRONMENT
from app.database import models
from app.database.database import engine, get_db
from app.dependencies import (
    logger, MEDIA_PATH, STATIC_PATH, templates)
from app.internal.quotes import daily_quotes, load_quotes
from app.internal.security.redirecting import on_after_register
from app.internal.security.security_main import (
    fastapi_users, jwt_authentication, my_exception_handler)
from app.routers import (
    agenda, calendar, categories, dayview, email,
    event, invitation, login, profile, register,
    search, telegram, whatsapp)
from app.telegram.bot import telegram_bot
from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session


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

origins = [
    "https://localhost:8000",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(register.router)
app.include_router(email.router)
app.include_router(invitation.router)
app.include_router(login.router)
app.include_router(
    fastapi_users.get_auth_router(
        jwt_authentication), prefix="/auth/jwt", tags=["auth"])
app.include_router(
    fastapi_users.get_auth_router(
        jwt_authentication), prefix="/logout", tags=["auth"])
app.include_router(
    fastapi_users.get_auth_router(
        jwt_authentication), prefix="/auth/cookie", tags=["auth"])
app.include_router(
    fastapi_users.get_register_router(
        on_after_register), prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_users_router(
        requires_verification=True), prefix="/users", tags=["users"])
app.include_router(
    fastapi_users.get_verify_router(
        "SECRET"), prefix="/auth", tags=["auth"])

app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, my_exception_handler)
load_quotes.load_daily_quotes(next(get_db()))

app.logger = logger

routers_to_include = [
    agenda.router,
    calendar.router,
    categories.router,
    dayview.router,
    email.router,
    event.router,
    invitation.router,
    login.router,
    profile.router,
    register.router,
    search.router,
    telegram.router,
    whatsapp.router,
]

for router in routers_to_include:
    app.include_router(router)

telegram_bot.set_webhook()


# TODO: I add the quote day to the home page
# until the relevant calendar view will be developed.
@app.get("/")
@logger.catch()
async def home(request: Request, db: Session = Depends(get_db)):
    quote = daily_quotes.quote_per_day(db)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
        "quote": quote
    })
