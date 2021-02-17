from fastapi import APIRouter, Request

from app.dependencies import templates


router = APIRouter()


@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about_us.html", {
        "request": request,
    })
