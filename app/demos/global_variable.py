from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.models import User
from app.dependencies import get_db, templates


router = APIRouter(
    prefix="/global-variable",
    tags=["global-variable"],
    responses={404: {"description": "Not found"}},
)


def create_test_logged_user(session: Session):
    user = User(
        username='test_user',
        email='my@email.po',
        password='1a2s3d4f5g6',
        full_name='My Name',
        language_id=1,
        telegram_id='',
    )

    user_query = session.query(User)
    user_from_db = user_query.filter_by(username=user.username).first()
    if not user_from_db:
        session.add(user)
        session.commit()
        user = session.query(User).filter_by(username=user.username).first()
    templates.env.globals['user'] = user


# The way it will be written on the page

# getting the logged in user
session = next(get_db())
create_test_logged_user(session)
user_from_db = session.query(User).filter_by(username="test_user").first()

# Placing a global variable
templates.env.globals['user'] = user_from_db


@router.get("/")
async def global_var(
    request: Request,
    test_session: Session = Depends(get_db)
):
    # for testing
    user_query = test_session.query(User)
    user_from_db = user_query.filter_by(username="test_user").first()
    templates.env.globals['user'] = user_from_db

    return templates.TemplateResponse("global_var_test.html", {
        "request": request
    })
