from datetime import datetime, timedelta
from typing import Union

from app.config import JWT_ALGORITHM, JWT_KEY, JWT_MIN_EXP
from passlib.context import CryptContext
from app.database.models import User
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidSignatureError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from .schema import LoginUser


pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="/login")


async def get_db_user_by_username(db: Session, username: str) -> User:
    """Checking database for user by username field"""
    user = db.query(User).filter_by(username=username).first()
    return user


def get_hashed_password(password: str) -> str:
    """Hashing user password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifying password and hashed password are equal"""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
        db: Session, user: LoginUser) -> Union[LoginUser, bool]:
    """Verifying user is in database and password is correct"""
    db_user = await get_db_user_by_username(db=db, username=user.username)
    if db_user and verify_password(user.password, db_user.password):
        return LoginUser(
            user_id=db_user.id,
            username=user.username, password=db_user.password)
    return False


def create_jwt_token(
        user: LoginUser, JWT_MIN_EXP: int = JWT_MIN_EXP,
        JWT_KEY: str = JWT_KEY) -> str:
    """Creating jwt-token out of user unique data"""
    expiration = datetime.utcnow() + timedelta(minutes=JWT_MIN_EXP)
    jwt_payload = {
        "sub": user.username,
        "user_id": user.user_id,
        "exp": expiration}
    jwt_token = jwt.encode(
        jwt_payload, JWT_KEY, algorithm=JWT_ALGORITHM)
    return jwt_token


async def check_jwt_token(
    db: Session,
        token: str = Depends(oauth_schema), path: bool = None) -> User:
    """
    Check whether JWT token is correct.
    Returns jwt payloads if correct.
    Raises HTTPException if fails to decode.
    """
    try:
        jwt_payload = jwt.decode(
            token, JWT_KEY, algorithms=JWT_ALGORITHM)
        return jwt_payload.get("sub"), jwt_payload.get("user_id")
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


async def get_cookie(request: Request) -> str:
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
    response = RedirectResponse(url=url)
    response.delete_cookie('Authorization')
    return response
