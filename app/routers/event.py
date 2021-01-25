from fastapi import APIRouter, Request

from app.internal.utilities import get_template_response

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return get_template_response("event/eventedit.html", request)


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    variables = {"event_id": id}
    return get_template_response("event/eventview.html", request, variables)
