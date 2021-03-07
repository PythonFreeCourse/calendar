from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_200_OK

from app.database.models import User
from app.dependencies import get_db
from app.internal.user.availability import disable, enable
from app.internal.utils import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_user(id: int, session=Depends(get_db)):
    user = session.query(User).filter_by(id=id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {id} not found",
        )
    return user


@router.get("/")
async def get_all_users(session=Depends(get_db)):
    return session.query(User).all()


@router.post("/disable")
def disable_logged_user(request: Request, session: Session = Depends(get_db)):
    """route that sends request to disable the user.
    after successful disable it will be directed to main page.
    if the disable fails user will stay at settings page
    and an error will be shown."""
    disable_successful = disable(session, get_current_user)
    if disable_successful:
        # disable succeeded- the user will be directed to homepage.
        url = router.url_path_for("home")
        return RedirectResponse(url=url, status_code=HTTP_200_OK)


@router.post("/enable")
def enable_logged_user(request: Request, session: Session = Depends(get_db)):
    """router that sends a request to enable the user.
    if enable successful it will be directed to main page.
    if it fails user will stay at settings page
    and an error will be shown."""
    enable_successful = enable(session, get_current_user)
    if enable_successful:
        # enable succeeded- the user will be directed to homepage.
        url = router.url_path_for("home")
        return RedirectResponse(url=url, status_code=HTTP_200_OK)
