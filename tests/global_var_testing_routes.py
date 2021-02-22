from sqlalchemy.orm import Session

from app.dependencies import get_db, templates
from app.internal.global_variable import set_global_user_var
from fastapi import APIRouter, Depends, Request


router = APIRouter(
    prefix="/global-variable",
    tags=["global-variable"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def global_var(request: Request, db: Session = Depends(get_db)):
    await set_global_user_var(request, db, templates)

    return templates.TemplateResponse("global_var_test.html", {
        "request": request
    })
