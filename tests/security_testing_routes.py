from app.dependencies import templates
from fastapi import APIRouter, Depends, Request
from app.internal.security.dependancies import (
    current_user_required, current_user, CurrentUser)

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
        request: Request, user: CurrentUser = Depends(current_user_required)):
    # This is how to protect route for logged in user only.
    # Dependency will return CurrentUser object.
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": user.username
    })


@router.get('/test_user')
async def user_route(
        request: Request, current_user: CurrentUser = Depends(current_user)):
    # This is how to get CurrentUser in a route.
    # Dependency will return CurrentUser object, or None if user not logged in.
    if current_user:
        message = "Hello " + current_user.username
    else:
        message = "No logged in user"
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": message
    })
