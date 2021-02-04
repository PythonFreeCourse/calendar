from fastapi import APIRouter, Depends, Request
from app.dependencies import templates
from app.internal.security.security_main import fastapi_users
from app.internal.security.security_schemas import User

router = APIRouter(
    prefix="",
    tags=["/login"],
    responses={404: {"description": "Not found"}},
)


@router.get("/login")
async def login_user_form(request: Request) -> templates:
    '''
    rendering register route get method
    '''
    return templates.TemplateResponse("login.html", {
        "request": request,
        "errors": None,
    })


# Not for production
@router.get("/protected")
async def protected_route(
        user: User = Depends(fastapi_users.get_current_active_user)):
    return user.username
    return "Hello, Protected"
