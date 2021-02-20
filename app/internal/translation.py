from typing import Optional

from fastapi import HTTPException, status
from iso639 import languages
from loguru import logger
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm.session import Session
from textblob import download_corpora, TextBlob
from textblob.exceptions import NotTranslated

from app.database.models import Language
from app.routers.user import get_users

download_corpora.download_all()


def translate_text_for_user(text: str, session: Session, user_id: int) -> str:
    """Translates text to the user's language setting.

    Args:
        text: The text in the original language.
        session: The database connection.
        user_id: The User's ID.

    Returns:
        The translated text.
    """
    target_lang = _get_user_language(user_id, session)
    if not target_lang:
        return text
    return translate_text(text, target_lang)


def translate_text(text: str,
                   target_lang: str,
                   original_lang: Optional[str] = None,
                   ) -> str:
    """Translates text to the target language.

    Args:
        text: The text in the original language.
        target_lang: The language to translate the text into.
        original_lang: Optional; The language of the text.

    Returns:
        The translated text.
    """
    if not text.strip():
        return ""
    if original_lang is None:
        language_code = _detect_text_language(text)
    else:
        language_code = _get_language_code(original_lang)

    if language_code == _get_language_code(target_lang):
        return text

    try:
        return str(TextBlob(text).translate(
            from_lang=language_code,
            to=_get_language_code(target_lang)))
    except NotTranslated:
        return text


def _get_user_language(user_id: int, session: Session) -> str:
    """Returns a user's language setting.

    Args:
        user_id: The User's ID.
        session: The database connection.

    Returns:
        The language name.

    Raises:
        HTTPException: If no language or multiple languages were
            found for the user.
    """
    try:
        user = get_users(session, id=user_id)[0]
    except IndexError:
        logger.exception("User was not found in the database.")
        return ""
    try:
        return _get_language_by_id(user.language_id, session)
    except (AttributeError, MultipleResultsFound, NoResultFound) as e:
        logger.critical(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error raised',
        )


def _detect_text_language(text: str) -> str:
    """Returns the language code of the language a given text is written in.

    The language is found using TextBlot to detect the language.
    TextBlot requires an internet connection.


    Args:
        text: The text in the original language.

    Returns:
        The language code of the language the text is written in.
    """
    return str(TextBlob(text).detect_language())


def _get_language_code(language_name: str) -> str:
    """Returns a language code from its language name.

    Args:
        language_name: The language name.

    Returns:
        The language code.
    """
    return languages.get(name=language_name.capitalize()).alpha2


def _get_language_by_id(language_id: int, session: Session) -> str:
    """Returns a language name from its ID.

    Args:
        language_id: The language ID.
        session: The database connection.

    Returns:
        The language name.
    """
    try:
        language = session.query(Language.name).filter_by(id=language_id).one()
    except (AttributeError, MultipleResultsFound, NoResultFound) as e:
        logger.critical(e)
        raise AttributeError(e)
    return language.name
