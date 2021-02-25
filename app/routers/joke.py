from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.internal import jokes

router = APIRouter()


@router.get("/joke")
async def joke(request: Request, db: Session = Depends(get_db)):
    return jokes.get_a_joke(db)
