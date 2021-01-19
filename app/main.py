from database import models, schemas
from database.database import engine, SessionLocal
from fastapi import Depends, FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/register", response_model=schemas.User)
def register_user_form(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "message": "register page"
    })


@app.post("/register", response_model=schemas.UserBase)
def register_user(request: Request, user: schemas.UserBase = Depends(schemas.UserCreate),  db: Session = Depends(get_db)):
    messages = []
    if type(user.confirm_password) is dict or type(user.email) is dict or type(user.username) is dict:
        if type(user.confirm_password) is dict:
            messages.append(user.confirm_password['message'])
        if type(user.email) is dict:
            messages.append(user.email['message'])
        if type(user.username) is dict:
            messages.append(user.username['message'])
    else:
        db_user_email = crud.get_user_by_email(db, email=user.email)
        db_user_username = crud.get_user_by_username(db, username=user.username)
        if db_user_username:
            messages.append("That username is already taken")
        if db_user_email:
            messages.append("Email already registered")
    if len(messages) > 0:
        return templates.TemplateResponse("register.html", {
        "request": request,
        "messages": messages,
        "status_code": 400
    })
    crud.create_user(db=db, user=user)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "User created",
        "status_code": 201
    })


@app.get("/delete")
def delete_user(db: Session = Depends(get_db)):
    crud.delete_user_by_mail(db=db, email="kobyfogel@gmail.com")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "Hello, World!"
    })
