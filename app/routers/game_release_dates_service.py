import datetime
from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from loguru import logger
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from starlette.templating import _TemplateResponse

import requests
from app.database.models import UserSettings
from app.dependencies import get_db, templates
from app.internal.security.dependencies import current_user
from app.internal.security.schema import CurrentUser
from app.internal.utils import create_model

# from typing import Dict, List, Union


router = APIRouter(
    prefix="/game-releases",
    tags=["game-releases"],
    responses={404: {"description": "Not found"}},
)


def is_user_signed_up_for_game_releases(
    session: Session,
    current_user_id: int,
):
    is_signed_up = (
        session.query(UserSettings)
        .filter(UserSettings.user_id == current_user_id)
        .filter(UserSettings.video_game_releases.is_(True))
        .first()
    )

    if is_signed_up:
        return True
    return False


# @router.post("/add-games-to-calendar")
# async def add_games_to_calendar(request: Request, session=Depends(get_db)):
#     current_user = get_current_user(session)
#     data = await request.form()

#     print(data)
#     for game in data:
#         print(game)
#         game_data = requests.get(
#             f"https://api.rawg.io/api/games/{game[0]}",
#         ).json()

#         create_event(
#             session,
#             title=game["name"],
#             start=game["release_date"],
#             end=game["release_date"],
#             owner_id=current_user.id,
#         )
#         print(game_data)


@router.post("/get_releases_by_dates")
async def fetch_released_games(request: Request, session=Depends(get_db)):
    data = await request.form()

    from_date = data["from_date"]
    to_date = data["to_date"]

    template = templates.get_template(
        "partials/calendar/feature_settings/games_list.html",
    )
    games = get_games_data(from_date, to_date)
    content = template.render(games=games)
    return HTMLResponse(content=content, status_code=HTTPStatus.OK)


@router.get("/get_game_releases_next_month")
def get_game_releases_month(request: Request):
    today = datetime.datetime.today()
    delta = datetime.timedelta(days=30)
    today_str = today.strftime("%Y-%m-%d")
    in_month_str = (today + delta).strftime("%Y-%m-%d")

    games = get_games_data(today_str, in_month_str)

    return games


# @router.post
# TODO
# add game to calendar
# @router.post
# remove game from calendar


def get_games_data(start_date, end_date):
    logger.debug((start_date, end_date))
    current_day_games = requests.get(
        f"https://api.rawg.io/api/games?dates={start_date},{end_date}",
    )
    current_day_games = current_day_games.json()["results"]
    games_data = []
    for result in current_day_games:
        current = {}
        current["name"] = result["name"]
        current["slug"] = result["slug"]
        current["platforms"] = []
        for platform in result["platforms"]:
            current["platforms"].append(platform["platform"]["name"])
        current["release_date"] = result["released"]
        games_data.append(current)

    return games_data


@router.get("/subscribe")
async def subscribe_game_release_service(
    request: Request,
    session: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
) -> _TemplateResponse:
    current_user_id = user.user_id

    if is_user_signed_up_for_game_releases(session, current_user_id):
        logger.debug("User already signed up for games")
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
    else:
        games_setting_true = {UserSettings.video_game_releases: True}
        games_setting_true_for_model = {
            "user_id": current_user_id,
            "video_game_releases": True,
        }
        current_user_settings = session.query(UserSettings).filter(
            UserSettings.user_id == current_user_id,
        )
        if current_user_settings:
            # TODO:
            # If all users are created with a UserSettings entry -
            # unnecessary check
            current_user_settings.update(games_setting_true)
            session.commit()
        else:
            create_model(session, UserSettings, **games_setting_true_for_model)
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)


@router.get("/unsubscribe")
async def unsubscribe_game_release_service(
    request: Request,
    session: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
) -> _TemplateResponse:
    current_user_id = user.user_id

    if not is_user_signed_up_for_game_releases(session, current_user_id):
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
    else:
        games_setting_false = {UserSettings.video_game_releases: False}
        games_setting_false_for_model = {
            "user_id": current_user_id,
            "video_game_releases": False,
        }
        current_user_settings = session.query(UserSettings).filter(
            UserSettings.user_id == current_user_id,
        )
        if current_user_settings:
            # TODO:
            # If all users are created with a UserSettings entry -
            # unnecessary check
            current_user_settings.update(games_setting_false)
            session.commit()
        else:
            create_model(
                session, UserSettings, **games_setting_false_for_model
            )
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
