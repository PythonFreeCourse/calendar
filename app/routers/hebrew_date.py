from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.internal import load_hebrew_view


router = APIRouter()


@router.get("/hebrewdate")
async def hebrew_date(request: Request, db: Session = Depends(get_db)):
    return load_hebrew_view.get_hebrew_dates(db)
