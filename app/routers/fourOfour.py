from app.dependencies import templates
from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter(
    prefix="/fourOfour",
    tags=["404"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def not_implemented(request: Request):
    return templates.TemplateResponse("fourOfour.j2",
                                      {"request": request})
