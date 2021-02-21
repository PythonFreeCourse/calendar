import json
from pathlib import Path
from typing import List, Optional, Tuple

from app.database.models import User, UserSettings
from app.dependencies import CURSORS_PATH, get_db, templates
from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm.session import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from app.internal.security.dependancies import current_user

router = APIRouter(
    prefix="/cursor",
    tags=["cursor"],
    responses={404: {"description": "Not found"}},
)


@router.get("/settings")
def cursor_settings(
    request: Request,
    user: User = Depends(current_user),
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
    user: User = Depends(current_user),
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


@router.get("/load_cursor")
async def load_cursor(
    session: Session = Depends(get_db),
    user: User = Depends(current_user),
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


def get_cursor_settings(
    session: Session,
    user_id: int,
) -> Tuple[Optional[List[str]], Optional[int], Optional[str], Optional[int]]:
    """Retrieves cursor settings from the database.

    Args:
        session (Session): the database.
        user_id (int, optional): the users' id.

    Returns:
        Tuple[str, Optional[List[str]], Optional[int],
        str, Optional[str], Optional[int]]: the cursor settings.
    """
    primary_cursor, secondary_cursor = None, None
    cursor_settings = (
        session.query(UserSettings).filter_by(user_id=user_id).first()
    )
    if cursor_settings:
        primary_cursor = cursor_settings.primary_cursor
        secondary_cursor = cursor_settings.secondary_cursor

    return primary_cursor, secondary_cursor


def save_cursor_settings(
    session: Session,
    user: User,
    cursor_choices: List[str],
):
    """Saves cursor choices in the db.

    Args:
        session (Session): the database.
        user (User): current user.
        cursor_choices (List[str]): primary and secondary cursors.
    """
    cursor_settings = (
        session.query(UserSettings).filter_by(user_id=user.user_id).first()
    )
    if cursor_settings:
        session.query(UserSettings).filter_by(
            user_id=cursor_settings.user_id,
        ).update(cursor_choices)
        session.commit()
    else:
        cursor_settings = UserSettings(user_id=user.user_id, **cursor_choices)
        session.add(cursor_settings)
        session.commit()
