import json
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.database.models import User
from app.dependencies import CURSORS_PATH, get_db, templates
from app.internal.cursor import get_cursor_settings, save_cursor_settings
from app.routers.profile import get_placeholder_user

router = APIRouter(
    prefix="/cursor",
    tags=["cursor"],
    responses={404: {"description": "Not found"}},
)


@router.get("/settings")
def cursor_settings(
    request: Request,
    user: User = Depends(get_placeholder_user),
    session: Session = Depends(get_db),
) -> templates.TemplateResponse:
    """A route to the cursor settings.

    Args:
        request (Request): the http request.
        session (Session): the database.

    Returns:
        templates.TemplateResponse: renders the cursor_settings.html page
        with the relevant information.
    """
    cursors = ["default"] + [
        path.stem for path in Path(CURSORS_PATH).glob("**/*.cur")
    ]

    return templates.TemplateResponse(
        "cursor_settings.html",
        {
            "request": request,
            "cursors": cursors,
        },
    )


@router.post("/settings")
async def get_cursor_choices(
    session: Session = Depends(get_db),
    user: User = Depends(get_placeholder_user),
    primary_cursor: str = Form(...),
    secondary_cursor: str = Form(...),
) -> RedirectResponse:
    """The form in which the user choses primary and secondary
    cursors.

    Args:
        session (Session, optional): the database.
        user (User, optional): [description]. temp user.
        primary_cursor (str, optional): name of the primary cursor.
        the primary cursor.
        secondary_cursor (str, optional): name of the secondary cursor.

    Returns:
        RedirectResponse: redirects to the homepage.
    """
    cursor_choices = {
        "primary_cursor": primary_cursor,
        "secondary_cursor": secondary_cursor,
    }
    save_cursor_settings(session, user, cursor_choices)

    return RedirectResponse("/", status_code=HTTP_302_FOUND)


@router.get("/load")
async def load_cursor(
    session: Session = Depends(get_db),
    user: User = Depends(get_placeholder_user),
) -> RedirectResponse:
    """loads cursors according to cursor settings.

    Args:
        session (Session): the database.
        user (User): the user.

    Returns:
        RedirectResponse: redirect the user to the homepage.
    """
    primary_cursor, secondary_cursor = get_cursor_settings(
        session,
        user.user_id,
    )

    return json.dumps(
        {
            "primary_cursor": primary_cursor,
            "secondary_cursor": secondary_cursor,
        },
    )
