import datetime

from app.dependencies import templates
from app.routers import calendar_gridcg as cg
from fastapi import Request

router = APIRouter(
    prefix="/calendar",
    tags=["calendar"],
    responses={404: {"description": "Not found"}},
)


@router.get("/calendar")
async def calendar(request: Request):
    date = datetime.date.today()
    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "calendar": {
                'date': date,
                'strf_date': cg.get_date_as_string(date),
                'days_of_the_week': cg.DAYS_OF_THE_WEEK,
                'month_block': cg.get_month_block(
                    datetime.date(date.year, date.month, 1)
                )
            }
        }
    )
