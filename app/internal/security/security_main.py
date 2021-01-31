from app.config import JWT_SECRET_KEY
from app.database.models import user_db
from app.internal.security.security_schemas import User, UserCreate, UserDB, UserUpdate
from fastapi_users.authentication import JWTAuthentication, CookieAuthentication
from fastapi_users import FastAPIUsers


auth_backends = []

jwt_authentication = JWTAuthentication(secret=JWT_SECRET_KEY, lifetime_seconds=3600)
cookie_authentication = CookieAuthentication(secret=JWT_SECRET_KEY, lifetime_seconds=500, name='my_cookie', cookie_httponly=True)
# auth_backends.append(jwt_authentication)
auth_backends.append(cookie_authentication)
#auth_backends,
fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
