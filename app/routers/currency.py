import datetime

from app.dependencies import templates
from app.internal.currency import is_valid_currency_api_response
from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/currency")
def today_currency(request: Request):
    """Current day currency router"""

    date = datetime.date.today().strftime("%Y-%m-%d")
    return currency(request, date)


@router.get("/currency/{date}")
def currency(request: Request, date: str):
    """Custom date currency router"""

    currency_resp = is_valid_currency_api_response(date)
    # TODO: get user default/preferred currency
    base = "USD"

    return templates.TemplateResponse("currency.html", {
        "request": request,
        "currency": currency_resp,
        "base": base,
        "date": date
    })
