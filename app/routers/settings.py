from fastapi import APIRouter, Request

from app.dependencies import templates


router = APIRouter(
    prefix="/settings",
    tags=["settings"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def settings(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
        },
    )
