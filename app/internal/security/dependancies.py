
from starlette.requests import Request
from fastapi import Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from app.internal.security.ouath2 import get_cookie, check_jwt_token


async def current_user_required(request: Request, jwt: str = Depends(get_cookie)):
    user = await check_jwt_token(jwt, path=request.url.path)
    # print(request.url)
    if user:
        return user
    else:
        return None

async def current_user(request: Request):
    if 'Authorization' in request.cookies:
        jwt = request.cookies['Authorization']
    else:
        return None
    user = await check_jwt_token(jwt, logged_in=True)
    print (user)
    return  user