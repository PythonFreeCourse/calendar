from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.dependencies import templates
from app.internal.celebrity import get_today_month_and_day

router = APIRouter()


@router.get("/celebrity")
def celebrity(request: Request) -> Response:
    """Returns the Celebrity page route.

    Args:
        request: The HTTP request.

    Returns:
        The Celebrity HTML page.
    """
    today = get_today_month_and_day()

    return templates.TemplateResponse("celebrity.html", {
        "request": request,
        "date": today,
    })
