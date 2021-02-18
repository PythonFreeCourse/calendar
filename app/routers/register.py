from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import _TemplateResponse

from app.internal.security.ouath2 import get_hashed_password
from app.database import schemas
from app.database import models
from app.dependencies import get_db, templates


router = APIRouter(
    prefix="",
    tags=["register"],
    responses={404: {"description": "Not found"}},
)


async def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    creating a new User object in the database, with hashed password
    """
    unhashed_password = user.password.encode("utf-8")
    hashed_password = get_hashed_password(unhashed_password)
    user_details = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "password": hashed_password,
        "description": user.description,
    }
    db_user = models.User(**user_details)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def check_unique_fields(
    db: Session,
    new_user: schemas.UserCreate,
) -> dict:
    """Verifying new user details are unique. Return relevant errors"""
    errors = {}
    if db.query(
        db.query(models.User)
        .filter(models.User.username == new_user.username)
        .exists(),
    ).scalar():
        errors["username"] = "That username is already taken"
    if db.query(
        db.query(models.User)
        .filter(models.User.email == new_user.email)
        .exists(),
    ).scalar():
        errors["email"] = "Email already registered"
    return errors


def get_error_messages_by_fields(
    errors: List[Dict[str, Any]],
) -> Dict[str, str]:
    """Getting validation errors by fields from pydantic ValidationError"""
    errors_by_fields = {error["loc"][0]: error["msg"] for error in errors}
    return {
        field_name: f"{field_name.capitalize()} {error_message}"
        for field_name, error_message in errors_by_fields.items()
    }


@router.get("/register")
async def register_user_form(request: Request) -> _TemplateResponse:
    """rendering register route get method"""
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "errors": None},
    )


@router.post("/register")
async def register(
    request: Request,
    db: Session = Depends(get_db),
) -> Union[_TemplateResponse, RedirectResponse]:
    """rendering register route post method."""
    form = await request.form()
    form_dict = dict(form)
    try:
        # creating pydantic schema object out of form data

        new_user = schemas.UserCreate(**form_dict)
    except ValidationError as e:
        # if pydantic validations fails, rendering errors to register.html
        errors = get_error_messages_by_fields(e.errors())
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "errors": errors, "form_values": form_dict},
        )
    errors = await check_unique_fields(db, new_user)
    if errors:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "errors": errors, "form_values": form_dict},
        )
    await create_user(db=db, user=new_user)
    return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
