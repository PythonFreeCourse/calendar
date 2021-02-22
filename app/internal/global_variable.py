from fastapi import Request

from app.dependencies import templates
from app.internal.security.ouath2 import (
    Session, get_jwt_token, get_authorization_cookie
)
from app.internal.security.schema import CurrentUser



async def get_user_for_global_var(db: Session, jwt: str) -> CurrentUser:
    jwt_payload = await get_jwt_token(db, jwt)
    username = jwt_payload.get("sub")
    user_id = jwt_payload.get("user_id")
    return CurrentUser(user_id=user_id, username=username)


async def set_global_user_var(request: Request, db: Session, temp: templates):
    jwt = await get_authorization_cookie(request)
    user = await get_user_for_global_var(db, jwt)
    temp.env.globals['user'] = user
