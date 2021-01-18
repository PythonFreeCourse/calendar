from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from dependencies import TEMPLATES_PATH

templates = Jinja2Templates(directory=TEMPLATES_PATH)

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("eventedit.html", {"request": request})
