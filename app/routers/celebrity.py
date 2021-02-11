from fastapi import APIRouter, Request

from app.dependencies import templates
from app.internal.celebrity import get_today_month_and_day

router = APIRouter()


@router.get("/celebrity")
def celebrity(request: Request):
    today = get_today_month_and_day()

    return templates.TemplateResponse("celebrity.html", {
        "request": request,
        "date": today
    })
