from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.datastructures import ImmutableMultiDict

from app.database.database import get_db
from app.database.models import Category

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


class CategoryModel(BaseModel):
    name: str
    color: str
    user_id: int


# TODO(issue#29): get current user_id from session
@router.get("/")
def get_categories(request: Request, db_session: Session = Depends(get_db)) -> List[Category]:
    if validate_request_params(request.query_params):
        return get_user_categories(db_session, **request.query_params)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Request {request.query_params} contains unallowed params.")


# TODO(issue#29): get current user_id from session
@router.post("/")
async def set_category(category: CategoryModel, db_session: Session = Depends(get_db)) -> Dict:
    try:
        cat = Category.create(db_session, name=category.name, color=category.color, user_id=category.user_id)
    except IntegrityError:
        db_session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"category is already exists for {category.user_id} user.")
    else:
        return {"category": cat.to_dict()}


def validate_request_params(query_params: ImmutableMultiDict) -> bool:
    """
    request.query_params contains not more than user_id, name, color and not less than user_id:
    Intersection must contain at least user_id.
    Union must not contain fields other than user_id, name, color.
    """
    all_fields = set(CategoryModel.schema()["required"])
    request_params = set(query_params)
    union_set = request_params.union(all_fields)
    intersection_set = request_params.intersection(all_fields)
    return union_set == all_fields and "user_id" in intersection_set


def get_user_categories(db_session: Session, user_id: int, **params) -> List[Category]:
    """
    Returns user's categories, filtered by params.
    """
    try:
        categories = db_session.query(Category).filter_by(user_id=user_id).filter_by(**params).all()
    except SQLAlchemyError:
        return []
    else:
        return categories
