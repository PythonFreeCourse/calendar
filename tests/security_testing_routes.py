from app.dependencies import templates
from fastapi import APIRouter, Depends, Request
from app.internal.security.dependancies import (
    is_logged_in, current_user, CurrentUser)

# from app.main import app
# app.include_router(security_testing_routes.router)


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
