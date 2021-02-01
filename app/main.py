from app.database import models
from app.database.database import engine
from app.dependencies import (
    MEDIA_PATH, STATIC_PATH, templates)
from app.routers import agenda, event, profile, email, invitation, register, login
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

####
from starlette.responses import RedirectResponse


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
app.include_router(login.router)

from app.internal.security.ouath2 import my_exception_handler
from starlette.status import HTTP_401_UNAUTHORIZED

app.add_exception_handler(HTTP_401_UNAUTHORIZED, my_exception_handler)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
