from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.models import User
from app.dependencies import get_db, templates


router = APIRouter(
    prefix="/global-variable",
    tags=["global-variable"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def global_var(request: Request, db: Session = Depends(get_db)):
    user = User(
        username='test_user',
        email='my@email.po',
        password='1a2s3d4f5g6',
        full_name='My Name',
        language_id=1,
        telegram_id='',
    )
    user_db = db.query(User).filter_by(username=user.username).first()
    if not user_db:
        db.add(user)
        db.commit()
        user = db.query(User).filter_by(username=user.username).first()
    templates.env.globals['user'] = user
    return templates.TemplateResponse("global_var_test.html", {
        "request": request
    })