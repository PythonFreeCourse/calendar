import re
from typing import Dict, List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.datastructures import ImmutableMultiDict
from starlette.templating import _TemplateResponse


from app.database.models import Category
from app.dependencies import get_db
from app.dependencies import templates

HEX_COLOR_FORMAT = r"^(?:[0-9a-fA-F]{3}){1,2}$"

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


class CategoryModel(BaseModel):
    name: str
    color: str
    user_id: int

    class Config:
        schema_extra = {
            "example": {
                "name": "Guitar lessons",
                "color": "aabbcc",
                "user_id": 1,
            }
        }


# TODO(issue#29): get current user_id from session
@router.get("/user", include_in_schema=False)
def get_categories(request: Request,
                   db_session: Session = Depends(get_db)) -> List[Category]:
    if validate_request_params(request.query_params):
        return get_user_categories(db_session, **request.query_params)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Request {request.query_params} contains "
                                   f"unallowed params.")


@router.get("/")
def category_color_insert(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("categories.html", {
        "request": request
    })


# TODO(issue#29): get current user_id from session
@router.post("/")
async def set_category(request: Request,
                       name: str = Form(None),
                       color: str = Form(None),
                       db_sess: Session = Depends(get_db)):

    message = ""
    user_id = 1    # until issue#29 will get current user_id from session
    color = color.replace('#', '')
    if not validate_color_format(color):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Color {color} if not from "
                                   f"expected format.")
    try:
        Category.create(db_sess, name=name, color=color, user_id=user_id)
    except IntegrityError:
        db_sess.rollback()
        message = "Category already exists"
        return templates.TemplateResponse("categories.html",
                                          dictionary_req(request, message,
                                                         name, color))
    message = f"Congratulation! You have created a new category: {name}"
    return templates.TemplateResponse("categories.html",
                                      dictionary_req(request, message,
                                                     name, color))


def validate_request_params(query_params: ImmutableMultiDict) -> bool:
    """
    request.query_params contains not more than user_id, name, color
    and not less than user_id:
    Intersection must contain at least user_id.
    Union must not contain fields other than user_id, name, color.
    """
    is_valid_color = True
    all_fields = set(CategoryModel.schema()["required"])
    request_params = set(query_params)
    union_set = request_params.union(all_fields)
    intersection_set = request_params.intersection(all_fields)
    if "color" in intersection_set:
        is_valid_color = validate_color_format(query_params["color"])
    return union_set == all_fields and "user_id" in intersection_set and (
        is_valid_color)


def validate_color_format(color: str) -> bool:
    """
    Validate color is from hex format (without `#`).
    """
    if color:
        return re.fullmatch(HEX_COLOR_FORMAT, color) is not None
    return False


def get_user_categories(db_session: Session,
                        user_id: int, **params) -> List[Category]:
    """
    Returns user's categories, filtered by params.
    """
    try:
        categories = db_session.query(Category).filter_by(
            user_id=user_id).filter_by(**params).all()
    except SQLAlchemyError:
        return []
    else:
        return categories


def dictionary_req(request, message, name, color) -> Dict:
    dictionary_tamplates = {
            "request": request,
            "message": message,
            "name": name,
            "color": color,
        }
    return dictionary_tamplates
