from app.internal.security.security_schemas import UserDB
from fastapi import Request


async def on_after_register(user: UserDB, request: Request):
    print(f"User {user.id} has registered.")
