from app.internal.security.dependancies import is_manager, is_logged_in
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


@router.get('/manager')
async def manager_route(
        request: Request, user: bool = Depends(is_manager)):
    # This is how to protect route for logged in manager only.
    # Dependency will return True.
    # if user not looged-in, or have no manager permission,
    # will be redirected to login route.
    return {"manager": user}
