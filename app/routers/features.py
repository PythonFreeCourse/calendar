from app.dependencies import templates
from app.internal.utils import get_current_user
from fastapi import APIRouter, Request, Depends
from starlette.responses import Response
from app.dependencies import get_db

router = APIRouter(
    prefix="/features",
    tags=["features"],
    responses={404: {"description": "Not found"}}
)


class Feature:
    """This class represent a feature in the app.

    Args:
        id      (int): The feature's id as it's in the db.
        icon    (str): Feature's icon name.
        name    (str): Feature's name.
        creator (str): Feature's creator username in the app.
        followers   (int): Integer represent how many users uses the feature.
        information (str): Information about the feature.
    """

    def __init__(self, id, icon, name, creator, followers, information):
        self.id = id
        self.icon = icon
        self.name = name
        self.creator = creator
        self.followers = followers
        self.information = information

    def __str__(self):
        return f"Feature {self.id}: {self.name.title()}, Created by: {self.creator}"


@router.get("/")
async def calendar(request: Request, session=Depends(get_db)) -> Response:
    user = get_current_user(session)
    return templates.TemplateResponse(
        "features.html",
        {
            "request": request,
            "features": {
                "installed": [
                    Feature(1, "bug-outline", "FEATURENAME", "Username",
                            0, "This is a test feature")
                ],
                "uninstalled": [
                    Feature(2, "bug-outline", "FEATURENAME", "Username",
                            0, "This is a test feature")
                ]
            }
        }
    )


@router.post("/add")
async def add(request: Request) -> Response:
    return True


@router.post("/delete")
async def add(request: Request) -> Response:
    return True
