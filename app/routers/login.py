from typing import Optional

from app.database.models import User
from app.dependencies import templates
from app.internal.security.dependancies import (
    current_user_required, current_user)
from app.internal.security.ouath2 import (
    authenticate_user, create_jwt_token, LoginUser)
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


router = APIRouter(
    prefix="",
    tags=["/login"],
    responses={404: {"description": "Not found"}},
)


@router.get("/login")
async def login_user_form(
        request: Request, message: Optional[str] = "") -> templates:
    '''rendering login route get method'''
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": message
    })


@router.post('/login')
async def login(
        request: Request,
        form: OAuth2PasswordRequestForm = Depends(),
        next: Optional[str] = "/") -> RedirectResponse:
    '''rendering login route post method.'''
    form_dict = {'username': form.username, 'hashed_password': form.password}
    user = LoginUser(**form_dict)
    '''
    Validaiting login form data,
    if user exist in database,
    if password correct.
    '''
    if user:
        user = await authenticate_user(user)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": 'Please check your credentials'
        })
    # creating HTTPONLY cookie with jwt-token out of user unique data
    jwt_token = create_jwt_token(user)
    response = RedirectResponse(next, status_code=HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=jwt_token,
        httponly=True,
    )
    return response


# Not for production
@router.get('/logout')
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    response.delete_cookie("Authorization")
    return response


# Not for production
@router.get('/protected')
async def protected_route(
        request: Request, user: User = Depends(current_user_required)):
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": user.username
    })


# Not for production
@router.get('/user')
async def user_route(
        request: Request, current_user: User = Depends(current_user)):
    if current_user:
        print(current_user.username)
    else:
        print(None)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "message": "user.username"
    })
