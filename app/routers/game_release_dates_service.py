import datetime
from typing import Dict, List

import requests
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.models import UserSettings
from app.dependencies import get_db, templates
from app.internal.game_releases_utils import (
    is_user_signed_up_for_game_releases,
)
from app.internal.security.dependencies import current_user
from app.internal.security.schema import CurrentUser
from app.internal.utils import create_model

router = APIRouter(
    prefix="/game-releases",
    tags=["game-releases"],
    responses={404: {"description": "Not found"}},
)


@router.post("/get_releases_by_dates")
async def fetch_released_games(
    request: Request,
    session=Depends(get_db),
) -> Response:
    data = await request.form()

    from_date = data["from-date"]
    to_date = data["to-date"]

    games = get_games_data(from_date, to_date)

    return templates.TemplateResponse(
        "partials/calendar/feature_settings/games_list.html",
        {"request": request, "games": games},
    )


@router.get("/next-month")
def get_game_releases_month(request: Request) -> List:
    today = datetime.datetime.today()
    delta = datetime.timedelta(days=30)
    today_str = today.strftime("%Y-%m-%d")
    in_month_str = (today + delta).strftime("%Y-%m-%d")

    return get_games_data(today_str, in_month_str)


def get_games_data(start_date: datetime, end_date: datetime) -> List[Dict]:
    API = "https://api.rawg.io/api/games"

    current_day_games = requests.get(
        f"{API}?dates={start_date},{end_date}",
    )
    current_day_games = current_day_games.json()["results"]
    games_data = []
    for result in current_day_games:
        current = {
            "name": result["name"],
            "slug": result["slug"],
            "platforms": [],
        }

        for platform in result["platforms"]:
            current["platforms"].append(platform["platform"]["name"])
        current["release_date"] = result["released"]
        games_data.append(current)

    return games_data


@router.post("/subscribe")
async def subscribe_game_release_service(
    request: Request,
    session: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
) -> Response:
    if is_user_signed_up_for_game_releases(session, user.user_id):
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
    games_setting_true_for_model = {
        "user_id": user.user_id,
        "video_game_releases": True,
    }
    current_user_settings = session.query(UserSettings).filter(
        UserSettings.user_id == user.user_id,
    )
    if current_user_settings:
        # TODO:
        # If all users are created with a UserSettings entry -
        # unnecessary check
        current_user_settings.update(games_setting_true_for_model)
        session.commit()
    else:
        create_model(session, UserSettings, **games_setting_true_for_model)
    return RedirectResponse("/profile", status_code=HTTP_302_FOUND)


@router.post("/unsubscribe")
async def unsubscribe_game_release_service(
    request: Request,
    session: Session = Depends(get_db),
    user: CurrentUser = Depends(current_user),
) -> RedirectResponse:
    current_user_id = user.user_id

    if not is_user_signed_up_for_game_releases(session, current_user_id):
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
    else:
        games_setting_false_for_model = {
            "user_id": str(current_user_id),
            "video_game_releases": False,
        }
        current_user_settings = session.query(UserSettings).filter(
            UserSettings.user_id == current_user_id,
        )
        if current_user_settings:
            # TODO:
            # If all users are created with a UserSettings entry -
            # unnecessary check
            current_user_settings.update(games_setting_false_for_model)
            session.commit()
        else:
            create_model(
                session, UserSettings, **games_setting_false_for_model
            )
        return RedirectResponse("/profile", status_code=HTTP_302_FOUND)
