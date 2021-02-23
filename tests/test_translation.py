from fastapi import HTTPException
from iso639 import languages
import pytest
from textblob import TextBlob

from app.internal.translation import (
    _detect_text_language, _get_language_code, _get_user_language,
    translate_text, translate_text_for_user
)

TEXT = [
    ("Привет мой друг", "english", "russian"),
    ("Hola mi amigo", "english", "spanish"),
    ("Bonjour, mon ami", "english", "french"),
    ("Hallo, mein Freund", "english", "german"),
]


@pytest.mark.parametrize("text, target_lang, original_lang", TEXT)
def test_translate_text_with_original_lang(text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert "Hello my friend" == answer
    assert TextBlob(text).detect_language() == languages.get(
        name=original_lang.capitalize()).alpha2
    assert TextBlob(answer).detect_language() == languages.get(
        name=target_lang.capitalize()).alpha2


@pytest.mark.parametrize("text, target_lang, original_lang", TEXT)
def test_translate_text_without_original_lang(
        text, target_lang, original_lang):
    answer = translate_text(text, target_lang)
    assert "Hello my friend" == answer
    assert TextBlob(answer).detect_language() == languages.get(
        name=target_lang.capitalize()).alpha2


@pytest.mark.parametrize("text, target_lang, original_lang", TEXT)
def test_translate_text_with_identical_original_and_target_lang(
        text, target_lang, original_lang):
    answer = translate_text(text, original_lang, original_lang)
    assert answer == text


@pytest.mark.parametrize("text, target_lang, original_lang", TEXT)
def test_translate_text_with_same_original_target_lang_without_original_lang(
        text, target_lang, original_lang):
    answer = translate_text(text, original_lang)
    assert answer == text


def test_translate_text_without_text_with_original_target_lang():
    answer = translate_text("", "english", "russian")
    assert answer == ""


def test_translate_text_without_text_without_original_lang():
    answer = translate_text("", "english")
    assert answer == ""


def test_get_language_code():
    answer = _get_language_code("english")
    assert answer == "en"


def test_get_user_language(user, session):
    user_id = user.id
    answer = _get_user_language(user_id, session=session)
    assert user_id == 1
    assert answer.lower() == "english"


@pytest.mark.parametrize("text, target_lang, original_lang", TEXT)
def test_translate_text_for_valid_user(
        text, target_lang, original_lang, session, user):
    user_id = user.id
    answer = translate_text_for_user(text, session, user_id)
    assert answer == "Hello my friend"


def test_translate_text_for_invalid_user(session, user):
    user_id = user.id
    answer = translate_text_for_user("Привет мой друг", session, user_id + 1)
    assert answer == "Привет мой друг"


def test_detect_text_language():
    answer = _detect_text_language("Hello my friend")
    assert answer == "en"


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Hoghhflaff", "english", "spanish"),
                          ("Bdonfdjourr", "english", "french"),
                          ("Hafdllnnc", "english", "german"),
                          ])
def test_translate_text_with_text_impossible_to_translate(
        text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert answer == text


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("@Здравствуй#мой$друг!", "english", "russian"),
                          ("@Hola#mi$amigo!", "english", "spanish"),
                          ("@Bonjour#mon$ami!", "english", "french"),
                          ("@Hallo#mein$Freund!", "english", "german"),
                          ])
def test_translate_text_with_symbols(text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert "@ Hello # my $ friend!" == answer


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Привет мой друг", "italian", "spanish"),
                          ("Hola mi amigo", "english", "russian"),
                          ("Bonjour, mon ami", "russian", "german"),
                          ("Ciao amico", "french", "german")
                          ])
def test_translate_text_with_with_incorrect_lang(
        text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert answer == text


def test_get_user_language_for_invalid_user(session, user):
    user_id = user.id + 1
    answer = _get_user_language(user_id, session=session)
    assert not answer


def test_get_user_language_for_invalid_language(session, user):
    user.language_id = 34
    session.commit()
    with pytest.raises(HTTPException):
        _get_user_language(user.id, session=session)
