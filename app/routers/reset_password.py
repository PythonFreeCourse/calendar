from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

from app.dependencies import get_db, templates
from app.internal.email import BackgroundTasks, send_reset_password_mail
from app.internal.security.ouath2 import (
    create_jwt_token,
    get_jwt_token,
    is_email_compatible_to_username,
    update_password,
)
from app.internal.security.schema import ForgotPassword, ResetPassword
from app.routers.login import router as login_router

router = APIRouter(
    prefix="",
    tags=["/reset_password"],
    responses={404: {"description": "Not found"}},
)


@router.get("/forgot-password")
async def forgot_password_form(request: Request) -> templates:
    """rendering forgot password form get method"""
    return templates.TemplateResponse(
        "forgot_password.html",
        {
            "request": request,
        },
    )


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> templates:
    """
    Validaiting form data fields.
    Validaiting form data against database records.
    If all validations succeed, creating jwt token,
    then sending email to the user with a reset password route link.
    The contains the verafiction jwt token.
    """
    form = await request.form()
    form_dict = dict(form)
    form_dict["username"] = "@" + form_dict["username"]
    try:
        # validating form data by creating pydantic schema object
        user = ForgotPassword(**form_dict)
    except ValidationError:
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "message": "Please check your credentials"},
        )
    user = await is_email_compatible_to_username(db, user)
    if not user:
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "message": "Please check your credentials"},
        )
    user.email_verification_token = create_jwt_token(user, jwt_min_exp=15)
    await send_reset_password_mail(user, background_tasks)
    return templates.TemplateResponse(
        "forgot_password.html",
        {
            "request": request,
            "message": "Email for reseting password was sent",
        },
    )


@router.get("/reset-password")
async def reset_password_form(
    request: Request,
    email_verification_token: Optional[str] = "",
) -> templates:
    """
    Rendering reset password form get method.
    Validating jwt token is supplied with request.
    """
    if email_verification_token:
        return templates.TemplateResponse(
            "reset_password.html",
            {
                "request": request,
            },
        )
    message = "?message=Verification token is missing"
    return RedirectResponse(
        login_router.url_path_for("login_user_form") + f"{message}",
        status_code=HTTP_302_FOUND,
    )


@router.post("/reset-password")
async def reset_password(
    request: Request,
    email_verification_token: str = "",
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """
    Receives email verification jwt token.
    Receives form data, and validates all fields are correct.
    Validating token.
    validatting form data against token details.
    If all validations succeed, hashing new password and updating database.
    """
    jwt_payload = get_jwt_token(email_verification_token)
    jwt_username = jwt_payload.get("sub").strip("@")
    form = await request.form()
    form_dict = dict(form)
    validated = True
    if not form_dict["username"] == jwt_username:
        validated = False
    try:
        # validating form data by creating pydantic schema object
        user = ResetPassword(**form_dict)
    except ValueError:
        validated = False
    if not validated:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "message": "Please check your credentials"},
        )
    await update_password(db, jwt_username, user.password)
    message = "?message=Success reset password"
    return RedirectResponse(
        login_router.url_path_for("login_user_form") + str(message),
        status_code=HTTP_302_FOUND,
    )
