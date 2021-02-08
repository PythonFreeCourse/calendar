from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status
from starlette.datastructures import ImmutableMultiDict
from starlette.templating import _TemplateResponse


from app.database.database import get_db
from tests.conftest import get_test_db
from app.database.models import Category
from app.dependencies import templates


router = APIRouter()


class CategoryModel(BaseModel):
    name: str
    color: str
    user_id: int

    class Config:
        schema_extra = {
            "example": {
                "name": "Guitar lessons",
                "color": "#aabbcc",
                "user_id": 1,
            }
        }


# TODO(issue#29): get current user_id from session
@router.get("/categories/by_parameters")
def get_categories(request: Request,
                   db_session: Session = Depends(get_db)) -> List[Category]:
    if validate_request_params(request.query_params):
        return get_user_categories(db_session, **request.query_params)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Request {request.query_params} contains "
                                   f"unallowed params.")


@router.get("/event/edit")
def your_categories(request: Request,
                    db_session: Session = Depends(get_db)) -> List[Category]:
    """
    will add all user categories to dropdown list
    """
    user_id = 1
    categories_list = get_user_categories(db_session, user_id)
    return templates.TemplateResponse("event/eventedit.html", {
        "request": request,
        "categories_list": categories_list,
    })


@router.get("/categories")
def category_color_insert(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("categories.html", {
        "request": request
    })


# TODO(issue#29): get current user_id from session
@router.post("/categories")
async def set_category(request: Request,
                       category_name: str = Form(None),
                       chosen_color: str = Form(None),
                       db_sess: Session = Depends(get_db)):

    message = ""
    user_id = 1    # until issue#29 will get current user_id from session
    try:
        Category.create(db_sess,
                        name=category_name,
                        color=chosen_color,
                        user_id=user_id)
    except IntegrityError:
        db_sess.rollback()
        message = "Category is already exists"
        return templates.TemplateResponse("categories.html", {
            "request": request,
            "message": message,
            "category_name": category_name,
            "chosen_color": chosen_color,
        })
    message = f"Congratulation! You have created the category: {category_name}"
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "message": message,
        "category_name": category_name,
        "chosen_color": chosen_color,
    })


def validate_request_params(query_params: ImmutableMultiDict) -> bool:
    """
    request.query_params contains not more than user_id, name, color
    and not less than user_id:
    Intersection must contain at least user_id.
    Union must not contain fields other than user_id, name, color.
    """
    all_fields = set(CategoryModel.schema()["required"])
    request_params = set(query_params)
    union_set = request_params.union(all_fields)
    intersection_set = request_params.intersection(all_fields)
    return union_set == all_fields and "user_id" in intersection_set


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


@router.post("/for_categories_test")
async def for_category_test(request: Request,
                            category_name: str = Form(None),
                            chosen_color: str = Form(None),
                            db_sess: Session = Depends(get_test_db)):
    """
    This route is only for run tests, user can't know this url and even
    if he will try he will get error: Method Not Allowed.
    """

    message = ""
    user_id = 1
    try:
        Category.create(db_sess,
                        name=category_name,
                        color=chosen_color,
                        user_id=user_id)
    except IntegrityError:
        db_sess.rollback()
        message = "category is already exists"
        return templates.TemplateResponse("categories.html", {
            "request": request,
            "message": message,
            "category_name": category_name,
            "chosen_color": chosen_color,
        })
    message = f"Congratulation! You have created the category {category_name}"
    return templates.TemplateResponse("categories.html", {
        "request": request,
        "message": message,
        "category_name": category_name,
        "chosen_color": chosen_color,
    })
