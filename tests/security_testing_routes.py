from app.dependencies import templates
from app.internal.security.dependancies import (
    CurrentUser, current_user, is_logged_in)
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
        request: Request, user: CurrentUser = Depends(is_logged_in)):
    # This is how to protect route for logged in user only.
    # Dependency will return CurrentUser object.
    return {"user": user.username}


@router.get('/test_user')
async def user_route(
        request: Request, current_user: CurrentUser = Depends(current_user)):
    # This is how to get CurrentUser in a route.
    # Dependency will return CurrentUser object, or None if user not logged in.
    if current_user:
        name = current_user.username
    else:
        name = "No logged in user"
    return {"user": name}
