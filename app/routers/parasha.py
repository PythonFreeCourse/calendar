from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session


from app.database.database import get_db
from app.internal import load_parasha



router = APIRouter()
@router.get("/parasha")

async def parasha(request: Request, db: Session = Depends(get_db)):
    return load_parasha.get_weekly_parasha(db)
