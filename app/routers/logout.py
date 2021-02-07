from fastapi import APIRouter, Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND


router = APIRouter(
    prefix="",
    tags=["/logout"],
    responses={404: {"description": "Not found"}},
)


@router.get('/logout')
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=HTTP_302_FOUND)
    response.delete_cookie("Authorization")
    return response
