from datetime import date
from io import BytesIO
from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.dependencies import get_db
from app.internal.agenda_events import get_events_in_time_frame
from app.internal.export import export_calendar

router = APIRouter(
    prefix="/export",
    tags=["export"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def export(
        start_date: Union[date, str],  # date or an empty string
        end_date: Union[date, str],
        db: Session = Depends(get_db),
) -> StreamingResponse:

    user_id = 1
    events = get_events_in_time_frame(start_date, end_date, user_id, db)
    file = BytesIO(export_calendar(db, list(events)))
    return StreamingResponse(
        content=file,
        media_type="text/calendar",
        headers={
            # change filename to "pylendar.ics"
            "Content-Disposition": "attachment;filename=pylendar.ics"
        },
    )
