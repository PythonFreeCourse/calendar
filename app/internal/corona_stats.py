import json
import random
from datetime import date, datetime
from typing import Any, Dict

import httpx
from fastapi import Depends
from loguru import logger
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.sqltypes import JSON

from app.database.models import CoronaStats
from app.dependencies import get_db

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
CORONA_API_URL = (
    "https://datadashboardapi.health.gov.il/api/queries/vaccinated"
)
user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)"
    " AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0)"
    " Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) "
    "Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko)"
    " Chrome/83.0.4103.97 Safari/537.36",
]

headers = {"User-Agent": random.choice(user_agent_list)}


def create_stats_object(corona_stats_data: JSON) -> CoronaStats:
    """ JSON -> DB Object """
    return CoronaStats(
        date_=datetime.strptime(
            corona_stats_data.get("Day_Date"),
            DATETIME_FORMAT,
        ),
        vaccinated=corona_stats_data.get("vaccinated"),
        vaccinated_cum=corona_stats_data.get("vaccinated_cum"),
        vaccinated_population_perc=corona_stats_data.get(
            "vaccinated_population_perc",
        ),
        vaccinated_second_dose=corona_stats_data.get(
            "vaccinated_seconde_dose",
        ),
        vaccinated_second_dose_cum=corona_stats_data.get(
            "vaccinated_seconde_dose_cum",
        ),
        vaccinated_second_dose_perc=corona_stats_data.get(
            "vaccinated_seconde_dose_population_perc",
        ),
    )


def serialize_stats(stats_object: CoronaStats) -> Dict[str, Any]:
    """ DB Object -> Dict """
    return {
        "vaccinated_second_dose_perc": (
            stats_object.vaccinated_second_dose_perc
        ),
        "vaccinated_second_dose_cum": (
            stats_object.vaccinated_second_dose_cum
        ),
    }


def serialize_dict_stats(stats_dict: Dict) -> Dict[str, Any]:
    """ api Dit -> pylender Dict """
    return {
        "vaccinated_second_dose_perc": (
            stats_dict.get("vaccinated_seconde_dose_population_perc")
        ),
        "vaccinated_second_dose_cum": (
            stats_dict.get("vaccinated_seconde_dose_cum")
        ),
    }


def save_corona_stats(
    corona_stats_data: JSON,
    db: Session = Depends(get_db),
) -> None:
    db.add(create_stats_object(corona_stats_data))
    db.commit()


def insert_to_db_if_needed(
    corona_stats_data: JSON,
    db: Session = Depends(get_db),
):
    """ gets the latest data inserted to gov database """
    latest_date = datetime.strptime(
        corona_stats_data.get("Day_Date"),
        DATETIME_FORMAT,
    )
    latest_saved = None
    try:
        latest_saved = (
            db.query(CoronaStats).order_by(desc(CoronaStats.date_)).one()
        )
    except NoResultFound:
        # on first system load, the table is empty
        save_corona_stats(corona_stats_data, db)
        return corona_stats_data

    if latest_saved is not None:
        # on more recent data arrival, we update the database
        if latest_saved.date_ < latest_date:
            save_corona_stats(corona_stats_data, db)
            return corona_stats_data
        else:
            return serialize_stats(latest_saved)


async def get_vacinated_data() -> JSON:
    async with httpx.AsyncClient() as client:
        res = await client.get(CORONA_API_URL, headers=headers)
        return json.loads(res.text)[-1]


def get_vacinated_data_from_db(db: Session = Depends(get_db)) -> CoronaStats:
    # I'm pulling once a day, it won't be the most updated data
    # but we dont want to be blocked for to many requests
    return (
        db.query(CoronaStats)
        .filter(func.date(CoronaStats.date_inserted) == date.today())
        .one()
    )


async def get_corona_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        db_data = get_vacinated_data_from_db(db)
        corona_stats_data = serialize_stats(db_data)

    except NoResultFound:
        try:
            response_data = await get_vacinated_data()
            insert_to_db_if_needed(response_data, db)
            corona_stats_data = serialize_dict_stats(response_data)
        except json.decoder.JSONDecodeError:
            corona_stats_data = {"error": "No data"}

    except (SQLAlchemyError, AttributeError) as e:
        logger.exception(f"corona stats failed with error: {e}")
        corona_stats_data = {"error": "No data"}
    return corona_stats_data
