from app.config import JWT_KEY
from app.database.models import user_db
from app.internal.security.security_schemas import (
    User, UserCreate, UserDB, UserUpdate)
from fastapi import Request, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    CookieAuthentication, JWTAuthentication)
from starlette.responses import RedirectResponse


auth_backends = []
jwt_authentication = JWTAuthentication(secret=JWT_KEY, lifetime_seconds=3600)
cookie_authentication = CookieAuthentication(
    secret=JWT_KEY, lifetime_seconds=500,
    name='my_cookie', cookie_httponly=True)
# auth_backends.append(jwt_authentication)
auth_backends.append(cookie_authentication)
fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)


async def my_exception_handler(
        request: Request,
        exc: status.HTTP_401_UNAUTHORIZED) -> RedirectResponse:
    next_url = f"next={request.url.path}"
    url = f"login?{next_url}"
    response = RedirectResponse(url=url)
    return response
