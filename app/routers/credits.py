from fastapi import APIRouter, Request
import json
from typing import List

from loguru import logger
from starlette.templating import _TemplateResponse

from app.config import RESOURCES_DIR
from app.dependencies import templates

router = APIRouter()


def credits_from_json() -> List:
    path = RESOURCES_DIR / "credits.json"
    try:
        with open(path, 'r') as json_file:
            json_list = json.load(json_file)
    except (IOError, ValueError):
        logger.exception(
            "An error occurred during reading of json file")
        return []
    return json_list


@router.get("/credits")
def credits(request: Request) -> _TemplateResponse:
    credit_list = credits_from_json()
    return templates.TemplateResponse("credits.html", {
        "request": request,
        "credit_list": credit_list
    })
