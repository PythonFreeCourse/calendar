from app.dependencies import templates
from fastapi import APIRouter, Request


router = APIRouter(
    prefix="",
    tags=["register"],
    responses={404: {"description": "Not found"}},
)


@router.get("/register")
async def register_user_form(request: Request) -> templates:
    '''
    rendering register route get method
    '''
    return templates.TemplateResponse("register.html", {
        "request": request,
        "errors": None
    })
