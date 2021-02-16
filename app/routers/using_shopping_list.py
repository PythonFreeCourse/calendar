from datetime import datetime

from fastapi import Depends, APIRouter, Form
from fastapi.encoders import jsonable_encoder
from requests import Session
from sqlalchemy.exc import SQLAlchemyError
from starlette import status
from starlette.responses import RedirectResponse, JSONResponse

from app.config import templates
from app.dependencies import get_db
from app.database.models import User
from app.internal.create_shopping_list import create_shopping_product, by_id

router = APIRouter(
    prefix="/shopping_product",
    tags=["shopping_product"],
    responses={404: {"description": "Not found"}},
)


@router.post("/delete")
def delete_shopping_product(
        shopping_product_id: int = Form(...),
        db: Session = Depends(get_db)
):
    # TODO: Check if the user is the owner of the shopping product.
    shopping_product = by_id(db, shopping_product_id)
    datestr = shopping_product.date.strftime('%Y-%m-%d')
    try:
        # Delete shopping product
        db.delete(shopping_product)

        db.commit()

    except (SQLAlchemyError, TypeError):
        return templates.TemplateResponse(
            "dayview.html", {"shopping_product_id": shopping_product_id},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # TODO: Send them a cancellation notice
        # if the deletion is successful
    return RedirectResponse(
        url=f"/day/{datestr}", status_code=302)


@router.post("/add")
async def add_shopping_product(name: str = Form(...),
                               amount: int = Form(...),
                               datestr: str = Form(...),
                               session=Depends(get_db)):
    # TODO: add a login session
    user = session.query(User).filter_by(username='test_username').first()
    create_shopping_product(
        session, name, amount,
        datetime.strptime(datestr, '%Y-%m-%d').date(), user.id
    )
    return RedirectResponse(f"/day/{datestr}", status_code=303)


@router.post("/edit")
async def edit_shopping_product(shopping_product_id: int = Form(...),
                                name: str = Form(...),
                                amount: int = Form(...),
                                datestr: str = Form(...),
                                session=Depends(get_db)):
    shopping_product = by_id(session, shopping_product_id)
    shopping_product.name = name
    shopping_product.amount = amount
    shopping_product.date = datetime.strptime(datestr, '%Y-%m-%d').date()
    session.commit()
    return RedirectResponse(f"/day/{datestr}", status_code=303)


@router.post("/setBought/{shopping_product_id}")
async def set_shopping_product_has_bought(
        shopping_product_id: int,
        session=Depends(get_db)
):
    shopping_product = by_id(session, shopping_product_id)
    shopping_product.is_bought = True
    session.commit()
    return RedirectResponse(
        f"/day/{shopping_product.date.strftime('%Y-%m-%d')}",
        status_code=303
    )


@router.post("/setUnBought/{shopping_product_id}")
async def set_shopping_product_has_not_bought(
        shopping_product_id: int, session=Depends(get_db)):
    shopping_product = by_id(session, shopping_product_id)
    shopping_product.is_bought = False
    session.commit()
    return RedirectResponse(
        f"/day/{shopping_product.date.strftime('%Y-%m-%d')}",
        status_code=303)


@router.get("/{shopping_product_id}")
async def get_shopping_product(shopping_product_id, session=Depends(get_db)):
    shopping_product = by_id(session, shopping_product_id)
    data = jsonable_encoder(shopping_product)
    return JSONResponse(content=data)
