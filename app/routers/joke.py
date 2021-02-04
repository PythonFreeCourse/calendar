from fastapi import APIRouter, Depends, Request
from app.internal import jokes
from sqlalchemy.orm import Session
from app.database.database import get_db


router = APIRouter()

@router.get("/joke")
async def joke(request: Request, db: Session = Depends(get_db)):
    joke = jokes.have_a_joke(db)
    return joke
