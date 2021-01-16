from fastapi import BackgroundTasks, Depends, FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.database.database import Base, SessionLocal, engine
from app.internal.email import send

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"

    })


@app.get("/profile")
def profile(request: Request):

    # Get relevant data from database
    upcouming_events = range(5)
    current_username = "Chuck Norris"
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "username": current_username,
        "events": upcouming_events
    })


@app.post("/emailbackground")
async def send_in_background(
    db: Session = Depends(get_db),
    send_to: str = "/",
    title: str = Form(...),
    event_used: str = Form(...),
    user_to_send: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks
) -> RedirectResponse:
    send(
        title=title, event_used=event_used,
        user_to_send=user_to_send,
        background_tasks=background_tasks, sessions=db)

    return RedirectResponse(send_to, status_code=303)
