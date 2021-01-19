import datetime

from app.routers import calendar_gridcg as cg
from app.dependencies import templates

from fastapi import Request


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
