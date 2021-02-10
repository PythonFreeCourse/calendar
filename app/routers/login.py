from typing import Optional, Union

from app.dependencies import get_db, templates
from app.internal.security.dependancies import (
    User, current_user)
from app.internal.security.ouath2 import (
    authenticate_user, create_jwt_token, LoginUser)
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


router = APIRouter(
    prefix="",
    tags=["/login"],
    responses={404: {"description": "Not found"}},
)


@router.get("/login")
async def login_user_form(
        request: Request, message: Optional[str] = "",
        current_user: Union[User, None] = Depends(current_user)) -> templates:
    """rendering login route get method"""
    if current_user:
        return RedirectResponse(url='/')
    return templates.TemplateResponse("login.html", {
        "request": request,
        "message": message,
        'current_user': current_user
    })


@router.post('/login')
async def login(
        request: Request,
        next: Optional[str] = "/",
        db: Session = Depends(get_db),
        existing_jwt: Union[str, bool] = False) -> RedirectResponse:
    """rendering login route post method."""
    form = await request.form()
    form_dict = dict(form)
    # creating pydantic schema object out of form data

    user = LoginUser(**form_dict)
    """
    Validaiting login form data,
    if user exist in database,
    if password correct.
    """
    if user:
        user = await authenticate_user(db, user)
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": 'Please check your credentials'
        })
    # creating HTTPONLY cookie with jwt-token out of user unique data
    # for testing
    if not existing_jwt:
        jwt_token = create_jwt_token(user)
    else:
        jwt_token = existing_jwt

    response = RedirectResponse(next, status_code=HTTP_302_FOUND)
    response.set_cookie(
        "Authorization",
        value=jwt_token,
        httponly=True,
    )
    return response
