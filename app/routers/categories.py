import re
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.datastructures import ImmutableMultiDict

from app.database.models import Category
from app.dependencies import get_db

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
@router.get("/", include_in_schema=False)
def get_categories(request: Request,
                   db_session: Session = Depends(get_db)) -> List[Category]:
    if validate_request_params(request.query_params):
        return get_user_categories(db_session, **request.query_params)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Request {request.query_params} contains "
                                   f"unallowed params.")


@router.get("/list")
def get_all_categories(
        db_session: Session = Depends(get_db)) -> List[Category]:
    return db_session.query(Category).all()


@router.get("/")
def get_categories_by_user_id(
        user_id: int, db_session: Session = Depends(get_db)
) -> List[Category]:
    return get_user_categories(db_session, user_id)


# TODO(issue#29): get current user_id from session
@router.post("/")
async def set_category(category: CategoryModel,
                       db_sess: Session = Depends(get_db)) -> Dict[str, Any]:
    if not validate_color_format(category.color):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Color {category.color} if not from "
                                   f"expected format.")
    try:
        cat = Category.create(db_sess,
                              name=category.name,
                              color=category.color,
                              user_id=category.user_id)
    except IntegrityError:
        db_sess.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"category is already exists for "
                                   f"user {category.user_id}.")
    else:
        return {"category": cat.to_dict()}


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
