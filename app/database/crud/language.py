"""CRUD functions for the Language model."""
from typing import List, Optional

from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from app.database.crud import crud
from app.database.models_v2 import Language as LanguageOrm
from app.database.schemas_v2 import Language


def get_by_id(session: Session, language_id: int) -> Optional[Language]:
    """Returns a Language by an ID.

    Args:
        session: The database connection.
        language_id: The language's ID.

    Returns:
        A Language if successful, otherwise returns None.
    """
    keywords = {LanguageOrm.id.key: language_id}
    language = crud.get_database_model_by_parameter(
        session, LanguageOrm, **keywords
    )
    if isinstance(language, LanguageOrm):
        return Language.from_orm(language)
    return None


def get_all(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Language]:
    """Returns all Languages.

    Args:
        session: The database connection.
        skip: The starting index.
            Defaults to 0.
        limit: The amount of returned items.
            Defaults to 100.

    Returns:
        A list of Languages.
    """
    languages = crud.get_all_database_models(session, LanguageOrm, skip, limit)
    return parse_obj_as(List[Language], languages)
