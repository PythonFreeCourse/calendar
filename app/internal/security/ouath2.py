from passlib.context import CryptContext
from .schema import LoginUser
from app.database.models import User
from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import templates
from app.database.database import SessionLocal 
from fastapi.security import OAuth2PasswordBearer
from datetime import  datetime, timedelta
import jwt
from starlette.status import HTTP_401_UNAUTHORIZED
from app.config import JWT_ALGORITHM, JWT_SECRET_KEY
from starlette.requests import Request

from starlette.responses import RedirectResponse


JWT_MIN_EXP = 3
pwd_context = CryptContext(schemes=["bcrypt"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="/login")


async def get_db_user_by_username(username: str):
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
async def authenticate_user(user: LoginUser):
    db_user = await get_db_user_by_username(username = user.username)
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
async def check_jwt_token(token: str = Depends(oauth_schema), logged_in=False, path=None):
    try:
        jwt_payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        jwt_username = jwt_payload.get("sub")
        jwt_hashed_password = jwt_payload.get("hashed_password")
        jwt_expiration = jwt_payload.get("exp")
        # if time.time() < jwt_expiration:
        db_user = await get_db_user_by_username(username=jwt_username)
        if db_user and db_user.password == jwt_hashed_password:
            return db_user
        else:
            return HTTPException(status_code=HTTP_401_UNAUTHORIZED, headers=path, detail="Your token is incorrect. Please log in again")
    except Exception as e:
        if logged_in:
            print("ff")
            return None
        if type(e).__name__ == 'ExpiredSignatureError':
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, headers=path, detail="Your token has expired. Please log in again")
        if type(e).__name__ == 'DecodeError':
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, headers=path, detail="Your token is incorrect. Please log in again")
        

######
async def get_cookie(request: Request):
    if 'Authorization' in request.cookies:
        return request.cookies['Authorization']
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, headers=request.url.path, detail="Please log in to enter this page")


async def my_exception_handler(request: Request, exc: HTTP_401_UNAUTHORIZED) -> RedirectResponse:
    paramas = f"?next={exc.headers}&message={exc.detail}"
    url = f"/login{paramas}"
    response = RedirectResponse(url=url)
    response.delete_cookie('Authorization')
    return response