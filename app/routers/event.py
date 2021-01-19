from fastapi import APIRouter, Request

from app.dependencies import templates


router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("eventedit.html", {"request": request})
