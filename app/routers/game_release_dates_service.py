import json
import requests
import datetime
from typing import Any, Dict, List, Union

from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import _TemplateResponse

from app.database import models
from app.database.models import Event, User, UserEvent, UserSettings
from app.dependencies import get_db, templates
from app.internal.utils import get_current_user, create_model


router = APIRouter(
    prefix="/game-releases",
    tags=["game-releases"],
    responses={404: {"description": "Not found"}},
)


def is_user_signed_up_for_game_releases(
        session: Session, current_user_id: int):
    is_signed_up = session.query(UserSettings).filter(
        UserSettings.user_id == current_user_id).filter(
            UserSettings.video_game_releases.is_(True)).first()

    if is_signed_up:
        return True
    return False


@router.post("/get_releases_by_dates")
async def fetch_released_games(
        request: Request, session=Depends(get_db)):
    current_user = get_current_user(session)
    data = await request.form()
    
    from_date = data['from_date']
    to_date = data['to_date']

    template = templates.get_template(
        'partials/calendar/feature_settings/game_release_modal.html'
    )
    games = get_games_data(from_date, to_date)
    content = template.render(games=games)
    return HTMLResponse(content=content, status_code=HTTPStatus.OK)
    # return from_date, to_date
    # url = router.url_path_for("get_game_releases_month")
    # return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/get_game_releases")
def get_game_releases_month(request: Request):
    today = datetime.datetime.today()
    delta = datetime.timedelta(days=30)
    today_str = today.strftime("%Y-%m-%d")
    in_month_str = (today+delta).strftime("%Y-%m-%d")
    template = templates.get_template(
        'partials/calendar/feature_settings/game_release_modal.html'
    )
    games = get_games_data(today_str, in_month_str)
    content = template.render(games=games)
    return HTMLResponse(content=content, status_code=HTTPStatus.OK)
    # return get_games_data(today_str, in_month_str)


# @router.post
# TODO
# add game to calendar
# @router.post
# remove game from calendar
def get_games_data(start_date, end_date):
    current_day_games = requests.get(
        f"https://api.rawg.io/api/games?dates={start_date},{end_date}").json()["results"]
    games_data = []
    for result in current_day_games:
        current = {}
        current["name"] = result["name"]
        current["platforms"] = []
        for platform in result["platforms"]:
            current["platforms"].append(platform["platform"]["name"])
        current["release_date"] = result["released"]
        games_data.append(current)

    return games_data


@router.get("/subscribe")
async def subscribe_game_release_service(
        request: Request,
        session: Session = Depends(get_db)) -> _TemplateResponse:
    current_user_id = get_current_user(session).id

    if is_user_signed_up_for_game_releases(session, current_user_id):
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
    else:
        games_setting_true = {UserSettings.video_game_releases: True}
        games_setting_true_for_model = {
            'user_id': current_user_id, 'video_game_releases': True}
        current_user_settings = session.query(UserSettings).filter(
            UserSettings.user_id == current_user_id)
        if current_user_settings:
            # TODO:
            # If all users are created with a UserSettings entry, unnecessary check
            current_user_settings.update(games_setting_true)
            session.commit()
        else:
            create_model(session, UserSettings, **games_setting_true_for_model)
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)


@router.get("/unsubscribe")
async def unsubscribe_game_release_service(
        request: Request,
        session: Session = Depends(get_db)) -> _TemplateResponse:
    current_user_id = get_current_user(session).id

    if not is_user_signed_up_for_game_releases(session, current_user_id):
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
    else:
        games_setting_false = {UserSettings.video_game_releases: False}
        games_setting_false_for_model = {
            'user_id': current_user_id, 'video_game_releases': False}
        current_user_settings = session.query(UserSettings).filter(
            UserSettings.user_id == current_user_id)
        if current_user_settings:
            # TODO:
            # If all users are created with a UserSettings entry, unnecessary check
            current_user_settings.update(games_setting_false)
            session.commit()
        else:
            create_model(session, UserSettings, **
                         games_setting_false_for_model)
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
