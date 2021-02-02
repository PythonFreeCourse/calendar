from app.dependencies import templates
from fastapi import APIRouter
from starlette.requests import Request

router = APIRouter(
    prefix="/404",
    tags=["404"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def not_implemented(request: Request):
    return templates.TemplateResponse("four_o_four.j2",
                                      {"request": request})
