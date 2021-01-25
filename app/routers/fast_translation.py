from fastapi import APIRouter, Depends, Request
# from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.database import get_db
# from app.dependencies import templates
from app.internal.fast_content_translation import fast_content_translation

router = APIRouter()


@router.post("/translation")
def fast_translation(db: Session = Depends(get_db)):
    user_id = 1
    fast_content_translation(session=db, user_id=user_id)
    pass
