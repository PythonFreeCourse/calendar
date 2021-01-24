from fastapi import APIRouter, Request

from app.dependencies import templates
from app.internal import languages

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    result = {"request": request}
    result.update(languages.get_translation_words())
    return templates.TemplateResponse("event/eventedit.html", result)


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    result = {"request": request, "event_id": id}
    result.update(languages.get_translation_words())
    return templates.TemplateResponse("event/eventview.html", result)
