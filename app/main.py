import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app.config import templates
from app.database.database import engine
from app.database.models import Base
from app.routers import invitation

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(invitation.invitation)

Base.metadata.create_all(bind=engine)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })


@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcoming_events = range(5)
    current_username = "Chuck Norris"

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcoming_events,
    })


if __name__ == '__main__':
    uvicorn.run(app)
