from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import _TemplateResponse

from app.database import schemas
from app.dependencies import get_db, templates
from app.internal.user.user import check_unique_fields, create_user

router = APIRouter(
    prefix="",
    tags=["register"],
    responses={404: {"description": "Not found"}},
)


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


def get_error_messages_by_fields(
    errors: List[Dict[str, Any]],
) -> Dict[str, str]:
    """Getting validation errors by fields from pydantic ValidationError"""
    errors_by_fields = {error["loc"][0]: error["msg"] for error in errors}
    return {
        field_name: f"{field_name.capitalize()} {error_message}"
        for field_name, error_message in errors_by_fields.items()
    }
