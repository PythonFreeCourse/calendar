from datetime import datetime, timedelta
from typing import Union

from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidSignatureError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND, HTTP_401_UNAUTHORIZED
from . import schema

from app.config import JWT_ALGORITHM, JWT_KEY, JWT_MIN_EXP
from app.database.models import User


pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="/login")


async def update_password(
        db: Session, db_user: User, user_password: str) -> None:
    """Updating User password in database"""
    hashed_password = get_hashed_password(user_password)
    db_user.password = hashed_password
    db.commit()
    return


def get_hashed_password(password: str) -> str:
    """Hashing user password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifying password and hashed password are equal"""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
        db: Session, user: Union[schema.LoginUser, schema.ForgotPassword],
        email: bool = False) -> Union[
            schema.LoginUser, schema.ForgotPassword, bool]:
    """
    Verifying database record by username.
    Comparing other given details to database record,
    varies with which function called this action.
    """
    db_user = await User.get_by_username(db=db, username=user.username)
    if not db_user:
        return False
    if email:
        if db_user.email == user.email:
            return schema.ForgotPassword(
                    username=user.username,
                    user_id=db_user.id, email=db_user.email)
        return False
    elif verify_password(user.password, db_user.password):
        return schema.LoginUser(
            user_id=db_user.id, is_manager=db_user.is_manager,
            username=user.username, password=db_user.password)
    return False


def create_jwt_token(
        user: schema.LoginUser, jwt_min_exp: int = JWT_MIN_EXP,
        jwt_key: str = JWT_KEY) -> str:
    """Creating jwt-token out of user unique data"""
    expiration = datetime.utcnow() + timedelta(minutes=jwt_min_exp)
    jwt_payload = {
        "sub": user.username,
        "user_id": user.user_id,
        "is_manager": user.is_manager,
        "exp": expiration}
    jwt_token = jwt.encode(
        jwt_payload, jwt_key, algorithm=JWT_ALGORITHM)
    return jwt_token


async def check_jwt_token(
    db: Session,
        token: str = Depends(oauth_schema), path: bool = None,
        manager: bool = False) -> User:
    """
    Check whether JWT token is correct.
    Returns jwt payloads if correct.
    Raises HTTPException if fails to decode.
    """
    try:
        jwt_payload = jwt.decode(
            token, JWT_KEY, algorithms=JWT_ALGORITHM)
        if not manager:
            return True
        if jwt_payload.get("is_manager"):
            return True
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=path,
                detail="You don't have a permition to enter this page")
    except InvalidSignatureError:
        raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=path,
                detail="Your token is incorrect. Please log in again")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            headers=path,
            detail="Your token has expired. Please log in again")
    except jwt.DecodeError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            headers=path,
            detail="Your token is incorrect. Please log in again")


async def get_authorization_cookie(request: Request) -> str:
    """
    Extracts jwt from HTTPONLY cookie, if exists.
    Raises HTTPException if not.
    """
    if 'Authorization' in request.cookies:
        return request.cookies['Authorization']
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        headers=request.url.path,
        detail="Please log in to enter this page")


async def auth_exception_handler(
        request: Request,
        exc: HTTP_401_UNAUTHORIZED) -> RedirectResponse:
    """
    Whenever HTTP_401_UNAUTHORIZED is raised,
    redirecting to login route, with original requested url,
    and details for why original request failed.
    """
    paramas = f"?next={exc.headers}&message={exc.detail}"
    url = f"/login{paramas}"
    response = RedirectResponse(url=url, status_code=HTTP_302_FOUND)
    response.delete_cookie('Authorization')
    return response
