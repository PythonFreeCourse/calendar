from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.dependencies import get_db, templates
from app.internal.security.ouath2 import (
    is_email_compatible_to_username, get_jwt_token,
    create_jwt_token, update_password)
from app.internal.email import (
    BackgroundTasks, send_reset_password_mail)
from app.internal.security.schema import (
    ForgotPassword, ResetPassword)


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
        user = await is_email_compatible_to_username(db, user)
        if user:
            user.email_verification_token = create_jwt_token(
                user, jwt_min_exp=15)
            await send_reset_password_mail(user, background_tasks)
            return templates.TemplateResponse("forgot_password.html", {
                "request": request,
                "message": "Email for reseting password was sent"})
    return templates.TemplateResponse("forgot_password.html", {
            "request": request,
            "message": 'Please check your credentials'
        })


@router.get("/reset-password")
async def reset_password_form(
        request: Request, email_verification_token: Optional[str] = ""
        ) -> templates:
    """
    Rendering reset password form get method.
    Validating jwt token is supplied with request.
    """
    if email_verification_token:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
        })
    message = "?message=Verification token is missing"
    return RedirectResponse(f"/login{message}")


@router.post("/reset-password")
async def reset_password(
        request: Request, email_verification_token: str = "",
        db: Session = Depends(get_db)
        ) -> RedirectResponse:
    '''
    Receives email verification jwt token.
    Receives form data, and validates all fields are correct.
    Validating token.
    validatting form data against token details.
    If all validations succeed, hashing new password and updating database.
    '''
    jwt_payload = await get_jwt_token(db, email_verification_token)
    jwt_username = jwt_payload.get("sub")
    form = await request.form()
    form_dict = dict(form)
    validated = True
    if not form_dict['username'] == jwt_username:
        validated = False
    try:
        # validating form data by creating pydantic schema object
        user = ResetPassword(**form_dict)
    except ValueError:
        validated = False
    if not validated:
        return templates.TemplateResponse("reset_password.html", {
            "request": request,
            "message": 'Please check your credentials'})
    await update_password(db, jwt_username, user.password)
    return RedirectResponse(
        url="/login?message=Success reset password",
        status_code=HTTP_302_FOUND)
