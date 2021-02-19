from typing import Union

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.database.models import User
from app.dependencies import get_db
from app.dependencies import templates


router = APIRouter(tags=["weight"],)


@router.get("/weight")
async def get_weight(
        request: Request,
        session: Session = Depends(get_db),
        target: Union[float, None] = None,
        current_weight: Union[float, None] = None,
        ):

    # TODO Waiting for user registration
    user_id = 1
    user = session.query(User).filter_by(id=user_id).first()
    target = user.target_weight
    if current_weight:
        return RedirectResponse(url='/')
    return templates.TemplateResponse("weight.html", {
        "request": request,
        "target": target,
        "current_weight": current_weight,
        }
    )


@router.post("/weight")
async def weight(
        request: Request,
        session: Session = Depends(get_db)):
    user_id = 1
    user = session.query(User).filter_by(id=user_id).first()
    data = await request.form()
    target = data['target']
    current_weight = data['current_weight']
    if target:
        user.target_weight = target
        session.commit()
    else:
        target = user.target_weight
        if not target:
            target = current_weight
    way_to_go = float(current_weight) - float(target)
    way_to_go = round(way_to_go, 2)
    if way_to_go > 0:
        way_message = f"Weight to lose: {way_to_go} Kg"
    elif way_to_go < 0:
        way_to_go = abs(way_to_go)
        way_message = f"Weight to add: {way_to_go} Kg"
    else:
        way_message = f"Great! You have reached your goal: {target} Kg"

    return templates.TemplateResponse("weight.html", {
        "request": request,
        "target": target,
        "current_weight": current_weight,
        "way_message": way_message
        }
    )
