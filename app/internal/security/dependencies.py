from typing import Optional

from fastapi import Depends, HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.database.models import User
from app.dependencies import get_db
from app.internal.security import schema
from app.internal.security.ouath2 import (
    Session,
    get_authorization_cookie,
    get_jwt_token,
)


async def is_logged_in(
    request: Request,
    db: Session = Depends(get_db),
    jwt: str = Depends(get_authorization_cookie),
) -> bool:
    """
    A dependency function protecting routes for only logged in user
    """
    jwt_payload = get_jwt_token(jwt)
    user_id = jwt_payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Your token is not valid. Please log in again",
        )
    return True


async def is_manager(
    request: Request,
    db: Session = Depends(get_db),
    jwt: str = Depends(get_authorization_cookie),
) -> bool:
    """
    A dependency function protecting routes for only logged in manager
    """
    jwt_payload = get_jwt_token(jwt)
    user_id = jwt_payload.get("user_id")
    if jwt_payload.get("is_manager") and user_id:
        return True
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        headers=request.url.path,
        detail="You don't have a permition to enter this page",
    )


async def current_user_from_db(
    request: Request,
    db: Session = Depends(get_db),
    jwt: str = Depends(get_authorization_cookie),
) -> User:
    """
    Returns logged in User object.
    A dependency function protecting routes for only logged in user.
    """
    jwt_payload = get_jwt_token(jwt)
    username = jwt_payload.get("sub")
    user_id = jwt_payload.get("user_id")
    db_user = await User.get_by_username(db, username=username)
    if db_user and db_user.id == user_id:
        return db_user
    else:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            headers=request.url.path,
            detail="Your token is incorrect. Please log in again",
        )


async def current_user(
    request: Request,
    db: Session = Depends(get_db),
    jwt: str = Depends(get_authorization_cookie),
) -> schema:
    """
    Returns logged in User object.
    A dependency function protecting routes for only logged in user.
    """
    jwt_payload = get_jwt_token(jwt)
    username = jwt_payload.get("sub")
    user_id = jwt_payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Your token is not valid. Please log in again",
        )
    return schema.CurrentUser(user_id=user_id, username=username)


def get_jinja_current_user(request: Request) -> Optional[schema.CurrentUser]:
    """Return the currently logged in user.
    Returns logged in User object if exists, None if not.
    Set as a jinja global parameter.
    """
    if "Authorization" not in request.cookies:
        return None
    jwt_payload = get_jwt_token(request.cookies["Authorization"])
    username = jwt_payload.get("sub")
    user_id = jwt_payload.get("user_id")
    return schema.CurrentUser(user_id=user_id, username=username)
