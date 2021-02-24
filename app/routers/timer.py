from typing import Dict, Optional

from fastapi import APIRouter, Depends, Request
from app.internal.security.dependancies import current_user, schema
from app.internal.timer import get_next_user_event_start_time
from app.dependencies import get_db


router = APIRouter()


@router.get("/timer")
def timer(
    request: Request,
    session=Depends(get_db),
    user: schema.CurrentUser = Depends(current_user)
) -> Dict[str, Optional[str]]:

    return get_next_user_event_start_time(session, user.user_id)
