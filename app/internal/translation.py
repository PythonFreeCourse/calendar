from typing import Optional

from fastapi import HTTPException
from iso639 import languages
from loguru import logger
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from starlette import status
from textblob import download_corpora, TextBlob
from textblob.exceptions import NotTranslated

from app.database.models import Language
from app.routers.user import get_users

download_corpora.download_all()


def translate_text(text: str,
                   target_lang: str,
                   original_lang: Optional[str] = None
                   ) -> str:
    """
    Translate text to the target language
    optionally given the original language
    """
    if not text.strip():
        return ""
    if original_lang is None:
        original_lang = _detect_text_language(text)
    else:
        original_lang = _lang_full_to_short(original_lang)

    if original_lang == _lang_full_to_short(target_lang):
        return text

    try:
        return str(TextBlob(text).translate(
            from_lang=original_lang,
            to=_lang_full_to_short(target_lang)))
    except NotTranslated:
        return text


def _detect_text_language(text: str) -> str:
    """
    Gets some text and returns the language it is in
    Uses external API
    """
    return str(TextBlob(text).detect_language())


def get_language_by_id(language_id: str, session: Session) -> str:
    """Get the language name by ID"""
    try:
        language = session.query(Language.name).filter_by(id=language_id).one()
    except (AttributeError, MultipleResultsFound, NoResultFound) as e:
        logger.critical(e)
        raise AttributeError(e)
    return language[0]


def _get_user_language(user_id: int, session: Session) -> str:
    """
    Gets a user-id and returns the language he speaks
    Uses the DB"""
    try:
        user = get_users(session, id=user_id)[0]
    except IndexError:
        logger.exception(
            "User was not found in the database."
        )
        return ""
    try:
        return get_language_by_id(user.language_id, session)
    except (AttributeError, MultipleResultsFound, NoResultFound) as e:
        logger.critical(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error raised')


def translate_text_for_user(text: str,
                            session: Session,
                            user_id: int) -> str:
    """
    Gets a text and a user-id and returns the text,
    translated to the language the user speaks
    """
    target_lang = _get_user_language(user_id, session)
    if not target_lang:
        return text
    return translate_text(text, target_lang)


def _lang_full_to_short(full_lang: str) -> str:
    """
    Gets the full language name and
    converts it to a two-letter language name
    """
    return languages.get(name=full_lang.capitalize()).alpha2
