import datetime

# from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND, HTTP_400_BAD_REQUEST

from app.dependencies import get_db, templates
from app.database.models import UserMenstrualPeriodLength
from app.internal.menstrual_predictor_utils import (
    add_3_month_predictions,
    is_user_signed_up_to_menstrual_predictor,
    generate_predicted_period_dates,
    remove_existing_period_dates,
)
from app.internal.utils import create_model, get_current_user

from loguru import logger


router = APIRouter(
    prefix="/menstrual_predictor",
    tags=["menstrual_predictor"],
    dependencies=[Depends(get_db)],
)

MENSTRUAL_PERIOD_CATEGORY_ID = 111


@router.get("/")
def join_menstrual_predictor(request: Request, db: Session = Depends(get_db)):
    current_user_id = get_current_user(db).id

    if not is_user_signed_up_to_menstrual_predictor(db, current_user_id):
        return templates.TemplateResponse(
            "join_menstrual_predictor.html",
            {
                "request": request,
            },
        )
    else:
        return RedirectResponse(url="/", status_code=HTTP_302_FOUND)


@router.get("/add-period-start/{start_date}")
def add_period_start(
    request: Request,
    start_date: str,
    db: Session = Depends(get_db),
):
    try:
        period_start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError as err:
        logger.exception(err)
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="The given date doesn't match a date format YYYY-MM-DD",
        )
    else:
        current_user_id = get_current_user(db).id
        user_period_length = is_user_signed_up_to_menstrual_predictor(
            db,
            current_user_id,
        )

        remove_existing_period_dates(db, current_user_id)
        if user_period_length:
            add_3_month_predictions(
                db,
                user_period_length,
                period_start_date,
                current_user_id,
            )
    logger.info("adding menstrual start date")
    return RedirectResponse("/", status_code=HTTP_302_FOUND)


@router.post("/")
async def submit_join_form(request: Request, db: Session = Depends(get_db)):

    data = await request.form()
    current_user = get_current_user(session=db)

    user_menstrual_period_length = {
        "user_id": current_user.id,
        "period_length": data["avg_period_length"],
    }
    last_period_date = datetime.datetime.strptime(
        data["last_period_date"],
        "%Y-%m-%d",
    )
    try:
        create_model(
            session=db,
            model_class=UserMenstrualPeriodLength,
            **user_menstrual_period_length,
        )
    except SQLAlchemyError:
        logger.info("Current user already signed up to the service, hurray")
        db.rollback()
    url = "/"
    generate_predicted_period_dates(
        db,
        data["avg_period_length"],
        last_period_date,
        current_user.id,
    )

    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)
