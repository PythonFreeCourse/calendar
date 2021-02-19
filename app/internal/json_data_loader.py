import json
import os
from typing import Any, Callable, Dict, List

from loguru import logger
from sqlalchemy.orm import Session

from app.database.models import Base, Quote, Zodiac
from app.internal import daily_quotes, zodiac


def load_to_database(session: Session) -> None:
    """Loads data from JSON data files into the database.

    On startup, data from the JSON files should be added to the database and
    not be accessed from a network call for each request as it is costly.

    The quotes JSON file content is copied from the free API:
    'https://type.fit/api/quotes'.

    Args:
        session: The database connection.
    """
    _insert_into_database(
        session,
        'app/resources/zodiac.json',
        Zodiac,
        zodiac.get_zodiac,
    )

    _insert_into_database(
        session,
        'app/resources/quotes.json',
        Quote,
        daily_quotes.get_quote,
    )


def _insert_into_database(
        session: Session,
        path: str,
        table: Base,
        model_creator: Callable
) -> bool:
    """Inserts the extracted JSON data into the database.

    Args:
        session: The database connection.
        path: The file path.
        table: A model entity table.
        model_creator: A model creation function.

    Returns:
        True if the save was successful, otherwise returns False.
    """
    if not _is_table_empty(session, table):
        return False

    json_objects = _get_data_from_json(path)
    model_objects = [model_creator(json_object)
                     for json_object in json_objects]
    session.add_all(model_objects)
    session.commit()
    return True


def _is_table_empty(session: Session, table: Base) -> bool:
    """Returns True if the table is empty.

    Args:
        session: The database connection.
        table: A model entity table.

    Returns:
        True if the table is empty, otherwise returns False.
    """
    return session.query(table).count() == 0


def _get_data_from_json(path: str) -> List[Dict[str, Any]]:
    """Returns a list of dictionary objects.

    Reads the data from a specific JSON file and converts the data into
    a list of dictionary items.

    Args:
        path: The file path.

    Returns:
        A list of dictionary objects.
    """
    try:
        with open(path, 'r') as json_file:
            json_content = json.load(json_file)
    except (IOError, ValueError):
        file_name = os.path.basename(path)
        logger.exception(
            f"An error occurred during reading of json file: {file_name}")
        return []
    return json_content
