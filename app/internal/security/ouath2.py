from passlib.context import CryptContext
# from app.database.schemas import Jwt_User
# from app.internal.crud import get_user_by_username
from starlette.responses import RedirectResponse
from .schema import LoginUser
from app.database.models import User
from sqlalchemy.orm.session import Session
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import templates
from app.database.database import get_db, SessionLocal 
from fastapi.security import OAuth2PasswordBearer
from datetime import  datetime, timedelta
import jwt
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_302_FOUND
import time
from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from starlette.requests import Request
from fastapi import Response


JWT_MIN_EXP = 3

pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="/login")

def get_db_user_by_username(username: str):
    session = SessionLocal()
    return session.query(User).filter_by(username = username).first()


def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        return False

# Authenticate username and password
def authenticate_user(user: LoginUser):
    db_user = get_db_user_by_username(username = user.username)
    if db_user:
        if verify_password(user.hashed_password, db_user.password):
            return LoginUser(username=user.username, hashed_password=db_user.password)
    return False


# Create access JWT token
def create_jwt_token(user: LoginUser):
    expiration = datetime.utcnow() + timedelta(minutes=JWT_MIN_EXP )
    jwt_payload = {"sub": user.username, "hashed_password": user.hashed_password, "exp": expiration}
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return jwt_token


# Check whether JWT token is correct
async def check_jwt_token(token: str = Depends(oauth_schema), logged_in=False):
    try:
        jwt_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        jwt_username = jwt_payload.get("sub")
        jwt_hashed_password = jwt_payload.get("hashed_password")
        jwt_expiration = jwt_payload.get("exp")
        if time.time() < jwt_expiration:
            db_user = get_db_user_by_username(username=jwt_username)
            if db_user and db_user.password == jwt_hashed_password:
                return db_user
        else:
            return HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    except Exception as e:
        if logged_in:
            return None
        if type(e).__name__ == 'ExpiredSignatureError':
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        if type(e).__name__ == 'DecodeError':
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
        


######
async def get_cookie(request: Request):
    if 'Authorization' in request.cookies:
        return request.cookies['Authorization']
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)


async def current_user(jwt: str = Depends(get_cookie)):
    user = await check_jwt_token(jwt)
    if user:
        return user
    else:
        return None

async def logged_in_user(request: Request):
    if 'Authorization' in request.cookies:
        jwt = request.cookies['Authorization']
    else:
        return None
    user = await check_jwt_token(jwt, logged_in=True)
    return  user
    
    