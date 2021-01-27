from app.database import models
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import agenda, event, profile, email, invitation, register
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")
app.mount("/media", StaticFiles(directory=MEDIA_PATH), name="media")

app.include_router(profile.router)
app.include_router(event.router)
app.include_router(agenda.router)
app.include_router(register.router)
app.include_router(email.router)
app.include_router(invitation.router)

##### fastapi_Users
from app.internal.security.security_main import fastapi_users, jwt_authentication
from app.internal.security.redirecting import on_after_register
from app.database.models import UserDB

# async def on_after_register(user: UserDB, request: Request):
    
#     print(f"User {user.id} has registered.")


app.include_router(
    fastapi_users.get_auth_router(jwt_authentication), prefix="/auth/jwt", tags=["auth"],)

app.include_router(
    fastapi_users.get_register_router(on_after_register),prefix="/auth",tags=["auth"],)

app.include_router(
    fastapi_users.get_users_router(requires_verification=True), prefix="/users", tags=["users"],)

app.include_router(
    fastapi_users.get_verify_router("SECRET"), prefix="/auth",tags=["auth"],)
##########

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
