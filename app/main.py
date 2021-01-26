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

# @app.middleware("http")
# async def add_middleware_here(request: Request, response: Response):
#     if str(request.url).__contains__("/login"):
#         return request
#         return RedirectResponse(
#             url="/login", status_code=200)
#     if "authorization" in response.headers:
#         token = response.headers["authorization"]
#     elif "authorization" in request.headers:
#         token = request.headers["authorization"]
#     if token:
#         response = request.url
#         response = RedirectResponse(
#             url=await request.url(request), status_code=200)
#         response.headers["authorization"] = token
#         return response
#     else:
#         return    


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!",
    })
