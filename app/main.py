from app.database import models
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.internal.security.redirecting import on_after_register
from app.internal.security.security_main import (
    fastapi_users, jwt_authentication, my_exception_handler)
from app.routers import (
    agenda, event, profile, email, invitation, register, login)
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


models.Base.metadata.create_all(bind=engine)

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
        on_after_register),prefix="/auth", tags=["auth"])
app.include_router(
    fastapi_users.get_users_router(
        requires_verification=True), prefix="/users", tags=["users"])
app.include_router(
    fastapi_users.get_verify_router(
        "SECRET"), prefix="/auth", tags=["auth"])

app.add_exception_handler(status.HTTP_401_UNAUTHORIZED, my_exception_handler)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
