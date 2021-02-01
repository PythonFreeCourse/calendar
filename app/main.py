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


from starlette.status import HTTP_401_UNAUTHORIZED
@app.exception_handler(HTTP_401_UNAUTHORIZED)
async def exception_handler(request: Request, exc: HTTP_401_UNAUTHORIZED) -> Response:
    response = RedirectResponse(url='/login')
    if exc.headers:
        response.set_cookie(
            "next_url", value=exc.headers, httponly=True)
    if exc.detail:
        response.set_cookie(
            "message", value=exc.detail, httponly=True)
    response.delete_cookie('Authorization')
    return response


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
