from fastapi import APIRouter, Depends, Request

from app.internal.security.dependancies import (
    current_user, current_user_from_db,
    is_logged_in, is_manager, User
)


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


@router.get('/is_logged_in')
async def is_logged_in(
        request: Request, user: bool = Depends(is_logged_in)):
    """This is how to protect route for logged in user only.
    Dependency will return True.
    if user not looged-in, will be redirected to login route.
    """
    return {"user": user}


@router.get('/is_manager')
async def is_manager(
        request: Request, user: bool = Depends(is_manager)):
    """This is how to protect route for logged in manager only.
    Dependency will return True.
    if user not looged-in, or have no manager permission,
    will be redirected to login route.
    """
    return {"manager": user}


@router.get('/current_user_from_db')
async def current_user_from_db(
        request: Request, user: User = Depends(current_user_from_db)):
    """This is how to protect route for logged in user only.
    Dependency will return User object.
    if user not looged-in, will be redirected to login route.
    """
    return {"user": user.username}


@router.get('/current_user')
async def current_user(
        request: Request, user: User = Depends(current_user)):
    """This is how to protect route for logged in user only.
    Dependency will return schema.CurrentUser object,
    contains user_id and username.
    if user not looged-in, will be redirected to login route.
    """
    return {"user": user.username}
