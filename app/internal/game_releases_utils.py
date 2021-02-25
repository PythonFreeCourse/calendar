from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import TYPE_CHECKING, List

import requests

if TYPE_CHECKING:
    from app.routers.calendar_grid import Day, Week


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
    games_by_dates = get_games_data_separated_by_days(
        start_date=first_day_str.strftime("%Y-%m-%d"),
        end_date=last_day_str.strftime("%Y-%m-%d"),
    )
    formatted_games = get_formatted_games_in_days(games_by_dates)
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


def get_games_data_separated_by_days(
    start_date: datetime,
    end_date: datetime,
) -> defaultdict[List]:
    API = "https://api.rawg.io/api/games"

    current_day_games = requests.get(
        f"{API}?dates={start_date},{end_date}",
    )
    current_day_games = current_day_games.json()["results"]
    games_data = defaultdict(list)
    for result in current_day_games:
        current = {}
        current["name"] = result["name"]
        if result["platforms"]:
            current["platforms"] = []
            for platform in result["platforms"]:
                current["platforms"].append(platform["platform"]["name"])
        ybd_release_date = translate_ymd_date_to_dby(result["released"])
        games_data[ybd_release_date].append(current)
    return games_data


def get_formatted_games_in_days(
    separated_games_dict: defaultdict[List],
    with_platforms: bool = False,
) -> defaultdict[List]:
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


def translate_ymd_date_to_dby(ymd_str: str) -> str:
    ymd_time = datetime.strptime(ymd_str, "%Y-%m-%d")
    return ymd_time.strftime("%d-%B-%Y")


def translate_dby_date_to_ymd(dby_str: str) -> str:
    dby_time = datetime.strptime(dby_str, "%d-%B-%Y")
    return dby_time.strftime("%Y-%m-%d")
