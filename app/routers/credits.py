from fastapi import APIRouter, Request
from starlette.templating import _TemplateResponse

from app.dependencies import templates

router = APIRouter()


@router.get("/credits")
def credits(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse("credits.html", {
        "request": request
    })
