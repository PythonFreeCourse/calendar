from typing import Union

from app.dependencies import get_db
from app.database.models import User
from app.internal.security.ouath2 import (
    Depends, Session, check_jwt_token,
    get_authorization_cookie, HTTP_401_UNAUTHORIZED,
    HTTPException)
from starlette.requests import Request


async def get_user(
        db: Session, user_id: int, username: str, path: str) -> User:
    '''
    Helper for dependency functions.
    Recives user details from decrypted jwt token,
    and check them against the database.
    returns User base model instance if succeeded,
    raises HTTPException if fails.
    '''
    db_user = await User.get_by_username(db, username=username)
    if db_user and db_user.id == user_id:
        return db_user
    else:
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=path,
                detail="Your token is incorrect. Please log in again")


async def is_logged_in(
    request: Request, db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie)) -> bool:
    """
    A dependency function protecting routes for only logged in user
    """
    await check_jwt_token(db, jwt)
    return True


async def logged_in_user(
    request: Request,
        db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie)) -> User:
    """
    A dependency function protecting routes for only logged in user.
    Returns logged in User object.
    """
    username, user_id = await check_jwt_token(db, jwt)
    return await get_user(db, user_id, username, request.url.path)


async def optional_logged_in_user(
    request: Request,
        db: Session = Depends(get_db)) -> Union[User, type(None)]:
    """
    A dependency function.
    Returns logged in User object if exists.
    None if not.
    """
    if 'Authorization' in request.cookies:
        jwt = request.cookies['Authorization']
    else:
        return None
    username, user_id = await check_jwt_token(db, jwt)
    return await get_user(db, user_id, username, request.url.path)
