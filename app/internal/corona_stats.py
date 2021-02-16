
import json
from datetime import date, datetime
from typing import Any, Dict

import requests
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
    'https://datadashboardapi.health.gov.il/api/queries/vaccinated'
)


def create_stats_object(data: JSON) -> CoronaStats:
    return CoronaStats(
        date_=datetime.strptime(
            data.get("Day_Date"),  DATETIME_FORMAT
        ),
        vaccinated=data.get("vaccinated"),
        vaccinated_cum=data.get(
            "vaccinated_cum"
        ),
        vaccinated_population_perc=data.get(
            "vaccinated_population_perc"
        ),
        vaccinated_seconde_dose=data.get(
            "vaccinated_seconde_dose"),
        vaccinated_seconde_dose_cum=data.get(
            "vaccinated_seconde_dose_cum"
        ),
        vaccinated_seconde_dose_population_perc=data.get(
            "vaccinated_seconde_dose_population_perc"
        )
    )


def serialize_stats(stats_object: CoronaStats) -> Dict:
    return {
        "vaccinated_seconde_dose_population_perc":
        stats_object.vaccinated_seconde_dose_population_perc,
        "vaccinated_seconde_dose_cum": stats_object.vaccinated_seconde_dose_cum
    }


def save_corona_stats(data: JSON, db: Session = Depends(get_db)) -> None:
    db.add(
        create_stats_object(data)
    )
    db.commit()


def insert_to_db_if_needed(data: JSON, db: Session = Depends(get_db)):
    """ gets the latest data inserted to gov database """
    latest_date = datetime.strptime(
        data.get("Day_Date"),  DATETIME_FORMAT
    )
    latest_saved = None
    try:
        latest_saved = (db.query(CoronaStats)
                        .order_by(desc(CoronaStats.date_))
                        .one())
    except NoResultFound:
        # on first system load, the table is empty
        save_corona_stats(data, db)
        return data

    if latest_saved is not None:
        # on more recent data arrival, we update the database
        if latest_saved.date_ < latest_date:
            save_corona_stats(data)
            return data
        else:
            return serialize_stats(latest_saved)


def get_vacinated_data() -> JSON:
    # the api updates during the day, so we want to stay updated.
    res = requests.get(CORONA_API_URL)
    return json.loads(res.text)[-1]


def get_vacinated_data_from_db(db: Session = Depends(get_db)) -> CoronaStats:
    return (db.query(CoronaStats).
            filter(
            func.date(CoronaStats.date_) == date.today()).
            one())


def get_corona_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        db_data = get_vacinated_data_from_db(db)
        data = serialize_stats(db_data)

    except NoResultFound:
        data = get_vacinated_data()
        insert_to_db_if_needed(data, db)

    except (SQLAlchemyError, AttributeError) as e:
        logger.error(f'corona stats failed with error: {e}')
        data = {'error': 'No data'}
    return data
