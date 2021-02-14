from starlette.requests import Request

from app.dependencies import get_db
from app.internal.security.ouath2 import (
    Depends, Session, check_jwt_token, get_authorization_cookie)


async def is_logged_in(
    request: Request, db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie)) -> bool:
    """
    A dependency function protecting routes for only logged in user
    """
    await check_jwt_token(db, jwt)
    return True


async def is_manager(
    request: Request, db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie)) -> bool:
    """
    A dependency function protecting routes for only logged in manager
    """
    await check_jwt_token(db, jwt, manager=True)
    return True
