from typing import List

from sqlalchemy.exc import SQLAlchemyError
from translate import Translator
from langdetect import detect

from app.database.database import SessionLocal
from app.database.models import Event, User

dictionary_of_languages = {
    "de": "german",
    "ru": "russian",
    "en": "english",
    "es": "spanish",
    "it": "italian",
    "fr": "french",
    "he": "hebrew"
}


def get_language_for_user(
        session: SessionLocal,
        user_id: int
        ) -> str:
    try:
        user = (
            session.query(User).filter(User.id == user_id).first()
            )
        language_for_user = user.language
    except SQLAlchemyError:
        return ""
    else:
        return language_for_user


def get_events_per_user(
        session: SessionLocal,
        user_id: int
        ) -> List[Event]:
    try:
        events = (
            session.query(Event).filter(Event.owner_id == user_id).all()
            )
    except SQLAlchemyError:
        return []
    else:
        return events


def get_language_content(content: str) -> str:
    return detect(content)


def find_language_in_dict(content: str) -> bool:
    return get_language_content(content) not in dictionary_of_languages.keys()


def compare_languages(language: str, content: str) -> bool:
    return dictionary_of_languages[get_language_content(content)] == language


def translation(language: str, content: str) -> str:
    translator = Translator(from_lang=dictionary_of_languages[get_language_content(content)], to_lang=language)
    translation_content = translator.translate(content)
    return translation_content


def add_translation_to_database(session: SessionLocal, event: Event, translation_content: str):
    event.translation_content = translation_content
    session.add(event)
    session.commit()
    session.close()  # ???


def fast_content_translation(session: SessionLocal, user_id: int) -> bool:
    language = get_language_for_user(session, user_id)
    if not language:
        return False
    events = get_events_per_user(session, user_id)
    if not events:
        return False
    for event in events:
        if event.content is None or event.translation_content is not None:
            return False
        content = event.content
        if compare_languages(language, content) and find_language_in_dict(content):
            return False
        else:
            translation_content = translation(language, content)
            add_translation_to_database(session, event, translation_content)
        return True
