from __future__ import annotations

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.routers.calendar_grid import Week, Day

from datetime import datetime

from collections import defaultdict

from loguru import logger

import requests

# from app.routers.calendar_grid import Week


def add_game_events_to_weeks(weeks: List["Week"], is_active: bool = True):
    if not is_active:
        return weeks
    first_week: Week = weeks[0]
    last_week: Week = weeks[-1]
    first_day: Day = first_week.days[0]
    last_day: Day = last_week.days[-1]
    first_day_str = datetime.strptime(first_day.set_id(), "%d-%B-%Y")
    last_day_str = datetime.strptime(last_day.set_id(), "%d-%B-%Y")
    games_released = get_games_data_separated_by_days(
        start_date=first_day_str.strftime("%Y-%m-%d"),
        end_date=last_day_str.strftime("%Y-%m-%d"),
    )
    for week in weeks:
        for day in week.days:
            if day.set_id() in games_released.keys():
                day.dailyevents.append(
                    (
                        f"GR!- {(games_released[day.set_id()][0])[:10]}",
                        (games_released[day.set_id()][0]),
                    ),
                )


def get_games_data_separated_by_days(start_date, end_date):
    logger.debug((start_date, end_date))
    current_day_games = requests.get(
        f"https://api.rawg.io/api/games?dates={start_date},{end_date}",
    )

    current_day_games = current_day_games.json()["results"]
    games_data = defaultdict(list)
    for result in current_day_games:
        current = {}
        current["name"] = result["name"]
        current["platforms"] = []
        for platform in result["platforms"]:
            current["platforms"].append(platform["platform"]["name"])
        ybd_release_date = translate_ymd_date_to_dby(result["released"])
        games_data[ybd_release_date].append(current)
    return get_formatted_games_in_days(games_data)


def get_formatted_games_in_days(
    separated_games_dict: dict,
    with_platforms: bool = False,
):
    formatted_games = defaultdict(list)

    for date, game_data in separated_games_dict.items():
        for game in game_data:
            formatted_game_str = ""
            formatted_game_str += game["name"]
            if with_platforms:
                formatted_game_str += "-Platforms-<br>"
                for platform in game["platforms"]:
                    formatted_game_str += f"{platform},"
            formatted_games[date].append(formatted_game_str)
    return formatted_games


def translate_ymd_date_to_dby(ymd_str: str):
    ymd_time = datetime.strptime(ymd_str, "%Y-%m-%d")
    return ymd_time.strftime("%d-%B-%Y")


def translate_dby_date_to_ymd(dby_str: str):
    dby_time = datetime.strptime(dby_str, "%d-%B-%Y")
    return dby_time.strftime("%Y-%m-%d")
