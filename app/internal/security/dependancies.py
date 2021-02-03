from typing import Union
from starlette.requests import Request
from fastapi import Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from app.internal.security.ouath2 import get_cookie, check_jwt_token, User


async def current_user_required(
    request: Request, jwt: str = Depends(get_cookie)) -> Union[User, bool]:
    '''A dependency function protecting routes for only logged in user'''
    user = await check_jwt_token(jwt, path=request.url.path)
    if user:
        return user


async def current_user(request: Request) -> Union[User, bool]:
    '''
    A dependency function.
    Returns logged in User object if exists.
    None if not.
    '''
    if 'Authorization' in request.cookies:
        jwt = request.cookies['Authorization']
    else:
        return None
    user = await check_jwt_token(jwt, logged_in=True)
    return  user