from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from typing import TYPE_CHECKING, Any, DefaultDict, Dict, List

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from app import config
from app.database.models import UserSettings

if TYPE_CHECKING:
    from app.routers.calendar_grid import Day, Week


def is_user_signed_up_for_game_releases(
    session: Session,
    current_user_id: int,
) -> bool:
    is_signed_up = bool(
        session.query(UserSettings)
        .filter(UserSettings.user_id == current_user_id)
        .filter(UserSettings.video_game_releases.is_(True))
        .first(),
    )

    return is_signed_up


def add_game_events_to_weeks(
    weeks: List["Week"],
    is_active: bool = True,
) -> List["Week"]:
    if not is_active:
        return weeks
    first_week: Week = weeks[0]
    last_week: Week = weeks[-1]
    first_day: Day = first_week.days[0]
    last_day: Day = last_week.days[-1]
    first_day_str = datetime.strptime(first_day.set_id(), "%d-%B-%Y")
    last_day_str = datetime.strptime(last_day.set_id(), "%d-%B-%Y")

    output = get_games_data_by_dates_from_api(
        start_date=first_day_str.strftime("%Y-%m-%d"),
        end_date=last_day_str.strftime("%Y-%m-%d"),
    )
    if not output["success"]:
        logger.exception("Unsuccessful RAWG API call")
        return weeks
    games_by_dates = output["results"]

    unformatted_games_by_dates = get_games_data_separated_by_dates(
        games_by_dates,
    )
    formatted_games = get_formatted_games_in_days(unformatted_games_by_dates)

    return insert_formatted_games_to_weeks(weeks, formatted_games)


def insert_formatted_games_to_weeks(
    weeks: List["Week"],
    formatted_games: DefaultDict[List[str]],
) -> List["Week"]:
    for week in weeks:
        for day in week.days:
            if day.set_id() in formatted_games.keys():
                for game in formatted_games[day.set_id()]:
                    day.dailyevents.append(
                        (
                            f"GR!- {(game)[:10]}",
                            (game),
                        ),
                    )
    return weeks


@lru_cache(maxsize=128)
def get_games_data_by_dates_from_api(
    start_date: str,
    end_date: str,
) -> Dict[str, Any]:
    API = "https://api.rawg.io/api/games"
    NO_API_RESPONSE = "The RAWG server did not response"
    input_query_string = {
        "dates": f"{start_date},{end_date}",
        "key": config.RAWG_API_KEY,
    }

    output: Dict[str, Any] = {}
    try:
        response = httpx.get(
            API,
            params=input_query_string,
        )
    except httpx.HTTPError:
        output["success"] = False
        output["error"] = NO_API_RESPONSE
        return output

    if response.status_code != httpx.codes.OK:
        output["success"] = False
        output["error"] = NO_API_RESPONSE
        return output

    output["success"] = True
    try:
        output.update(response.json())
        return output
    except KeyError:
        output["success"] = False
        output["error"] = response.json()["error"]["message"]
        return output


def get_games_data_separated_by_dates(
    api_data: Dict[str, Any],
) -> DefaultDict[List]:
    games_data = defaultdict(list)
    for result in api_data:
        current = {
            "name": result["name"],
            "platforms": [],
        }
        if result["platforms"]:
            for platform in result["platforms"]:
                current["platforms"].append(platform["platform"]["name"])
        ybd_release_date = translate_ymd_date_to_dby(result["released"])
        games_data[ybd_release_date].append(current)
    return games_data


def get_formatted_games_in_days(
    separated_games_dict: DefaultDict[List],
    with_platforms: bool = False,
) -> DefaultDict[List[str]]:
    formatted_games = defaultdict(list)

    for date, game_data in separated_games_dict.items():
        for game in game_data:
            formatted_game_str = format_single_game(game, with_platforms)
            formatted_games[date].append(formatted_game_str)
    return formatted_games


def format_single_game(raw_game: Dict, with_platforms: bool = False) -> str:
    formatted_game_str = ""
    formatted_game_str += raw_game["name"]
    if with_platforms:
        formatted_game_str += "-Platforms-<br>"
        for platform in raw_game["platforms"]:
            formatted_game_str += f"{platform},"
    return formatted_game_str


def translate_ymd_date_to_dby(ymd_str: str) -> str:
    ymd_time = datetime.strptime(ymd_str, "%Y-%m-%d")
    return ymd_time.strftime("%d-%B-%Y")


def translate_dby_date_to_ymd(dby_str: str) -> str:
    dby_time = datetime.strptime(dby_str, "%d-%B-%Y")
    return dby_time.strftime("%Y-%m-%d")
