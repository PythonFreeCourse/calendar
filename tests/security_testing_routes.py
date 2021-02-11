from app.internal.security.dependancies import (
    User, optional_logged_in_user, logged_in_user, is_logged_in)
from fastapi import APIRouter, Depends, Request


"""
These routes are for security testing.
They represent an example for how to use
security dependencies in other routes.
"""
router = APIRouter(
    prefix="",
    tags=["/security"],
    responses={404: {"description": "Not found"}},
)


@router.get('/protected')
async def protected_route(
        request: Request, user: bool = Depends(is_logged_in)):
    # This is how to protect route for logged in user only.
    # Dependency will return True.
    # if user not looged-in, will be redirected to login route.
    return {"user": user}


@router.get('/logged_in_user')
async def logged_in_user(
        request: Request, user: User = Depends(logged_in_user)):
    # This is how to protect route for logged in user only.
    # Dependency will return User object.
    # if user not looged-in, will be redirected to login route.
    return {"user": user.username}


@router.get('/test_user')
async def user_route(
        request: Request,
        current_user: User = Depends(optional_logged_in_user)):
    # This is how to get current_user in a route.
    # Dependency will return User object, or None if user not logged in.
    if current_user:
        name = current_user.username
    else:
        name = "No logged in user"
    return {"user": name}
