
import json
from datetime import date, datetime
from typing import Any, Dict
import requests
from fastapi import Depends
from loguru import logger
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.database.database import get_db
from app.database.models import WikipediaEvents


def get_vacinated_data(db: Session = Depends(get_db)):
    print('here')
    url = 'https://datadashboardapi.health.gov.il/api/queries/vaccinated'
    res = requests.get(url)
    data = json.loads(res.text)[-1]
    print(str(data.get("vaccinated_seconde_dose_population_perc")))
    return data


def get_corona_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    return get_vacinated_data(db)