from typing import Optional

from iso639 import languages
from sqlalchemy.exc import SQLAlchemyError
from textblob import TextBlob, download_corpora
from textblob.exceptions import NotTranslated

from app.database.database import SessionLocal
from loguru import logger
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


def _get_user_language(user_id: int, session: SessionLocal) -> str:
    """
    Gets a user-id and returns the language he speaks
    Uses the DB"""
    try:
        user = get_users(session, id=user_id)[0]
        language_user = user.language
    except SQLAlchemyError:
        logger.exception(
            "User of user preferred language was not found in the database."
        )
        return ""
    else:
        return language_user


def translate_text_for_user(text: str,
                            session: SessionLocal,
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
