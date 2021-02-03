from typing import Union
from passlib.context import CryptContext
from .schema import LoginUser
from app.database.models import User
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import templates
from app.database.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from starlette.requests import Request
from starlette.responses import RedirectResponse


JWT_MIN_EXP = 3
pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="/login")


async def get_db_user_by_username(username: str) -> User:
    '''Checking database for user by username field'''
    session = SessionLocal()
    return session.query(User).filter_by(username=username).first()


def get_hashed_password(password) -> str:
    '''Hashing user password'''
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    '''Verifying password and hashed password are equal'''
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        return False


async def authenticate_user(user: LoginUser) -> Union[LoginUser, bool]:
    '''Verifying user is in database and password is correct'''
    db_user = await get_db_user_by_username(username=user.username)
    if db_user:
        if verify_password(user.hashed_password, db_user.password):
            return LoginUser(
                username=user.username, hashed_password=db_user.password)
    return False


def create_jwt_token(user: LoginUser) -> str:
    '''Creating jwt-token out of user unique data'''
    expiration = datetime.utcnow() + timedelta(minutes=JWT_MIN_EXP)
    jwt_payload = {
        "sub": user.username,
        "hashed_password": user.hashed_password,
        "exp": expiration}
    jwt_token = jwt.encode(
        jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return jwt_token


async def check_jwt_token(
    token: str=Depends(oauth_schema),
        logged_in: bool=False, path: bool=None) -> Union[User, bool]:
    '''
    Check whether JWT token is correct. Returns User object if yes.
    Returns None or raises HTTPException,
    depanding which depandency activated this function.
    '''
    try:
        jwt_payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        jwt_username = jwt_payload.get("sub")
        jwt_hashed_password = jwt_payload.get("hashed_password")
        jwt_expiration = jwt_payload.get("exp")
        db_user = await get_db_user_by_username(username=jwt_username)
        if db_user and db_user.password == jwt_hashed_password:
            return db_user
        else:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=path,
                detail="Your token is incorrect. Please log in again")
    except Exception as e:
        if logged_in:
            return None
        if type(e).__name__ == 'ExpiredSignatureError':
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=path,
                detail="Your token has expired. Please log in again")
        if type(e).__name__ == 'DecodeError':
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                headers=path,
                detail="Your token is incorrect. Please log in again")
        

async def get_cookie(request: Request) -> str:
    '''
    Extracts jwt from HTTPONLY cookie, if exists.
    Raises HTTPException if not.
    '''
    if 'Authorization' in request.cookies:
        return request.cookies['Authorization']
    raise HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        headers=request.url.path,
        detail="Please log in to enter this page")


async def my_exception_handler(
        request: Request,
        exc: HTTP_401_UNAUTHORIZED) -> RedirectResponse:
    '''
    Whenever HTTP_401_UNAUTHORIZED is raised,
    redirecting to login route, with original requested url,
    and details for why original request failed.
    '''
    paramas = f"?next={exc.headers}&message={exc.detail}"
    url = f"/login{paramas}"
    response = RedirectResponse(url=url)
    response.delete_cookie('Authorization')
    return response
