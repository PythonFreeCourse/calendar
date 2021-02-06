from app.dependencies import templates
from app.internal.celebrity import get_today_month_and_day
from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/celebrity")
def search(request: Request):
    today = get_today_month_and_day()

    return templates.TemplateResponse("celebrity.html", {
        "request": request,
        "date": today
    })
