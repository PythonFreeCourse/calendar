import datetime

from fastapi import APIRouter, Request

from app.dependencies import templates

router = APIRouter()


# TODO: Add this as a feature to the calendar view/
#           day view/features panel frontend


@router.get("/currency")
def today_currency(request: Request):
    """Current day currency router"""

    date = datetime.date.today().strftime("%Y-%m-%d")
    return currency(request, date)


@router.get("/currency/{date}")
def currency(request: Request, date: str):
    """Custom date currency router"""

    # TODO: get user default/preferred currency
    base = "USD"

    return templates.TemplateResponse("currency.html", {
        "request": request,
        "base": base,
        "date": date
    })
