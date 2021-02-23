from fastapi import Depends, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.requests import Request

from app.database.models import User
from app.dependencies import get_db
from app.internal.security.ouath2 import (
    Session, get_jwt_token, get_authorization_cookie
)
from app.internal.security import schema


async def is_logged_in(
    request: Request, db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie)) -> bool:
    """
    A dependency function protecting routes for only logged in user
    """
    await get_jwt_token(db, jwt)
    return True


async def is_manager(
    request: Request, db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie)) -> bool:
    """
    A dependency function protecting routes for only logged in manager
    """
    jwt_payload = await get_jwt_token(db, jwt)
    if jwt_payload.get("is_manager"):
        return True
    raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=request.url.path,
                detail="You don't have a permition to enter this page")


async def current_user_from_db(
    request: Request,
    db: Session = Depends(get_db),
    jwt: str = Depends(get_authorization_cookie),
) -> User:
    """
    Returns logged in User object.
    A dependency function protecting routes for only logged in user.
    """
    jwt_payload = await get_jwt_token(db, jwt)
    username = jwt_payload.get("sub")
    user_id = jwt_payload.get("user_id")
    db_user = await User.get_by_username(db, username=username)
    if db_user and db_user.id == user_id:
        return db_user
    else:
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=request.url.path,
                detail="Your token is incorrect. Please log in again")


async def current_user(
    request: Request,
    db: Session = Depends(get_db),
    jwt: str = Depends(get_authorization_cookie),
) -> schema:
    """
    Returns logged in User object.
    A dependency function protecting routes for only logged in user.
    """
    jwt_payload = await get_jwt_token(db, jwt)
    username = jwt_payload.get("sub")
    user_id = jwt_payload.get("user_id")
    return schema.CurrentUser(user_id=user_id, username=username)
