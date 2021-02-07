from typing import Union

from app.internal.security.ouath2 import (
    Depends, Session, check_jwt_token, get_cookie, get_db)
from app.internal.security.schema import CurrentUser
from fastapi import Depends
from starlette.requests import Request


async def current_user_required(
        request: Request, 
        db: Session = Depends(get_db),
        jwt: str = Depends(get_cookie)) -> CurrentUser:
    """A dependency function protecting routes for only logged in user"""
    user = await check_jwt_token(db, jwt, path=request.url.path)
    if user:
        return user


async def current_user(
    request: Request,
    db: Session = Depends(get_db),) -> Union[CurrentUser, bool]:
    """
    A dependency function.
    Returns logged in User object if exists.
    None if not.
    """
    if 'Authorization' in request.cookies:
        jwt = request.cookies['Authorization']
    else:
        return None
    user = await check_jwt_token(db, jwt)
    return user
