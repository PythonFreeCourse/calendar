from starlette.requests import Request

from app.database.models import User
from app.dependencies import get_db
from app.internal.security.ouath2 import (
    Depends, Session, check_jwt_token, get_authorization_cookie,
    HTTPException, HTTP_401_UNAUTHORIZED)


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


async def current_user(
    request: Request,
        db: Session = Depends(get_db),
        jwt: str = Depends(get_authorization_cookie),
) -> User:
    """
    Returns logged in User object.
    A dependency function protecting routes for only logged in user.
    """
    username, user_id = await check_jwt_token(db, jwt)
    db_user = await User.get_by_username(db, username=username)
    if db_user and db_user.id == user_id:
        return db_user
    else:
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=request.url.path,
                detail="Your token is incorrect. Please log in again")
