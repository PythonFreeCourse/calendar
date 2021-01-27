from fastapi import Request
from app.internal.security.security_schemas import UserDB


async def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")