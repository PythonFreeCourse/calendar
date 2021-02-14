from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.templating import _TemplateResponse

from app.dependencies import get_db, templates
from app.internal import friend_view


router = APIRouter(tags=["friendview"])


@router.get("/friendview")
def friendview(
        request: Request,
        db: Session = Depends(get_db),
        my_friend: str = None,
) -> _TemplateResponse:

    user_id = 1
    events_list = friend_view.get_events_per_friend(db, user_id, my_friend)

    return templates.TemplateResponse("friendview.html", {
        "request": request,
        "events": events_list,
        "my_friend": my_friend,
    })
