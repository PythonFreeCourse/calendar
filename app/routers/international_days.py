from typing import Optional

from fastapi import APIRouter, Request, Depends
from datetime import date, datetime

from starlette.responses import JSONResponse

from app.database.database import get_db
from app.dependencies import templates
from app.internal.international_days.get_international_days import international_day_per_day

router = APIRouter(
    prefix="/international_day",
    tags=["international_days"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_international_day(datestr: str, session=Depends(get_db)):
    international_day = international_day_per_day(session, datetime.strptime(datestr, '%d-%m-%Y').date())
    dict_day = {
        "day": international_day.day,
        "month": international_day.month,
        "international_day": international_day.international_day
    }
    return JSONResponse(dict_day)