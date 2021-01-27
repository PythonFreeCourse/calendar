from app.config import JWT_SECRET_KEY
from app.database.models import user_db
from app.internal.security.security_schemas import User, UserCreate, UserDB, UserUpdate
from fastapi_users.authentication import JWTAuthentication
from fastapi_users import FastAPIUsers

SECRET = "SECRET"

auth_backends = []

jwt_authentication = JWTAuthentication(secret=JWT_SECRET_KEY, lifetime_seconds=3600)

auth_backends.append(jwt_authentication)

fastapi_users = FastAPIUsers(
    user_db,
    auth_backends,
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)
