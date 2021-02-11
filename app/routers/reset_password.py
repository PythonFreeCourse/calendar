from typing import Optional, Union

from app.dependencies import get_db, templates
from app.internal.security.dependancies import is_authenticated
from app.internal.security.ouath2 import (
    authenticate_user, check_jwt_token,
    create_jwt_token, update_password)
from app.internal.security.reset_password import (
    BackgroundTasks ,send_mail)
from app.internal.security.schema import (
    ForgotPassword, LoginUser, ResetPassword)
from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


router = APIRouter(
    prefix="",
    tags=["/reset_password"],
    responses={404: {"description": "Not found"}},
)


@router.get("/forgot-password")
async def forgot_password_form(
            request: Request) -> templates:
    """rendering forgot password form get method"""
    return templates.TemplateResponse("forgot_password.html", {
        "request": request,
    })


@router.post('/forgot-password')
async def forgot_password(
        request: Request, background_tasks: BackgroundTasks,
            db: Session = Depends(get_db)) -> templates:
    """
    Validaiting form data fields.
    Validaiting form data against database records.
    If all validations succeed, creating jwt token,
    then sending email to the user with a reset password route link.
    The contains the verafiction jwt token.
    """
    form = await request.form()
    form_dict = dict(form)
    try:
        # validating form data by creating pydantic schema object
        user = ForgotPassword(**form_dict)
    except ValidationError:
        user = False
    if user:
        user =  await authenticate_user(db, user, email=True)
        if user:
            user.token = create_jwt_token(user, JWT_MIN_EXP=15)
            await send_mail(db, user, background_tasks)
            return templates.TemplateResponse("forgot_password.html", {
                "request": request,
                "message": "Email for reseting password was sent"})
    return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": 'Please check your credentials'
        })


@router.get("/reset-password")
async def reset_password_form(
        request: Request, token: Optional[str] = ""
        ) -> templates:
    """
    Rendering reset password form get method.
    Validating jwt token is supplied with request.
    """
    if token:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
        })
    message = "?message=Verification token is missing"
    return RedirectResponse(f"/login{message}")


@router.post("/reset-password")
async def reset_password(
        request: Request, token: str = "",
        db: Session = Depends(get_db)
        ) -> RedirectResponse:
    '''
    Receives jwt token.
    Receives form data, and validates all fields are correct.
    Validating token.
    validatting form data against database records.
    validatting jwt details against database records.
    If all validations succeed, hashing new password and updating database.
    '''
    form = await request.form()
    form_dict = dict(form)
    db_user = await is_authenticated(request=request, db = db, jwt = token)
    validated = True
    if not form_dict['username'] == db_user.username:
        validated = False
    try:
        # validating form data by creating pydantic schema object
        user = ResetPassword(**form_dict)
    except ValueError:
        validated = False
    if not validated:
        return templates.TemplateResponse("reset_password.html", {
        "request": request,
        "message": 'Please check your credentials'
    })
    await update_password(db, db_user, user.password)
    return RedirectResponse(
        url="/login?message=Success reset password",
        status_code=HTTP_302_FOUND)
