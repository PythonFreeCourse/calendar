from app.dependencies import templates
from fastapi import APIRouter, Request
from starlette.templating import _TemplateResponse

router = APIRouter()


@router.get("/keyboard_shortcuts")
def keyboard_shortcuts(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("keyboard_shortcuts.html", {
        "request": request})
