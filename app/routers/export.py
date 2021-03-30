from datetime import date
from io import BytesIO
from typing import Union

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.internal.agenda_events import get_events_in_time_frame
from app.internal.export import get_icalendar_with_multiple_events
from app.internal.security.schema import CurrentUser
from tests.security_testing_routes import current_user

router = APIRouter(
    prefix="/export",
    tags=["export"],
    responses={status.HTTP_404_NOT_FOUND: {"description": _("Not found")}},
)


@router.get("/")
def export(
    start_date: Union[date, str],
    end_date: Union[date, str],
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
) -> StreamingResponse:
    """Returns the Export page route.

    Args:
        start_date: A date or an empty string.
        end_date: A date or an empty string.
        db: Optional; The database connection.
        user: user schema object.

    Returns:
        A StreamingResponse that contains an .ics file.
    """
    events = get_events_in_time_frame(start_date, end_date, user.user_id, db)
    file = BytesIO(get_icalendar_with_multiple_events(db, list(events)))
    return StreamingResponse(
        content=file,
        media_type="text/calendar",
        headers={
            # Change filename to "PyLendar.ics".
            "Content-Disposition": "attachment;filename=PyLendar.ics",
        },
    )
