from iso639 import languages
import pytest
from textblob import TextBlob

from fastapi import HTTPException
from starlette import status

from app.internal.translation import (_detect_text_language,
                                      _get_user_language, _lang_full_to_short,
                                      translate_text, translate_text_for_user)


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Привет мой друг", "english", "russian"),
                          ("Hola mi amigo", "english", "spanish"),
                          ("Bonjour, mon ami", "english", "french"),
                          ("Hallo, mein Freund", "english", "german"),
                          ])
@pytest.mark.translation
def test_translate_text_with_original_lang(text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert "Hello my friend" == answer
    assert TextBlob(text).detect_language() == languages.get(
        name=original_lang.capitalize()).alpha2
    assert TextBlob(answer).detect_language() == languages.get(
        name=target_lang.capitalize()).alpha2


@pytest.mark.parametrize("text, target_lang",
                         [("Привет мой друг", "english"),
                          ("Bonjour, mon ami", "english"),
                          ("Hallo, mein Freund", "english"),
                          ])
@pytest.mark.translation
def test_translate_text_without_original_lang(text, target_lang):
    answer = translate_text(text, target_lang)
    assert "Hello my friend" == answer
    assert TextBlob(answer).detect_language() == languages.get(
        name=target_lang.capitalize()).alpha2


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Привет мой друг", "russian", "russian"),
                          ("Hola mi amigo", "spanish", "spanish"),
                          ("Bonjour, mon ami", "french", "french"),
                          ("Hallo, mein Freund", "german", "german"),
                          ("Ciao amico", "italian", "italian")
                          ])
@pytest.mark.translation
def test_translate_text_with_same_original_target_lang_with_original_lang(
        text,
        target_lang,
        original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert answer == text


@pytest.mark.parametrize("text, target_lang",
                         [("Привет мой друг", "russian"),
                          ("Hola mi amigo", "spanish"),
                          ("Bonjour, mon ami", "french"),
                          ("Hallo, mein Freund", "german"),
                          ("Ciao amico", "italian")
                          ])
@pytest.mark.translation
def test_translate_text_with_same_original_target_lang_without_original_lang(
        text,
        target_lang):
    answer = translate_text(text, target_lang)
    assert answer == text


@pytest.mark.translation
def test_translate_text_without_text_with_original_target_lang():
    answer = translate_text("", "english", "russian")
    assert answer == ""


@pytest.mark.translation
def test_translate_text_without_text_without_original_lang():
    answer = translate_text("", "english")
    assert answer == ""


@pytest.mark.translation
def test_lang_short_to_full():
    answer = _lang_full_to_short("english")
    assert answer == "en"


@pytest.mark.translation
def test_get_user_language(user, session):
    user_id = user.id
    answer = _get_user_language(user_id, session=session)
    assert user_id == 1
    assert answer.lower() == "english"


@pytest.mark.parametrize("text", ["Привет мой друг",
                                  "Bonjour, mon ami",
                                  "Hello my friend"]
                         )
@pytest.mark.translation
def test_translate_text_for_good_user(text, user, session):
    user_id = user.id
    answer = translate_text_for_user(text, session, user_id)
    assert answer == "Hello my friend"


@pytest.mark.translation
def test_translate_text_for_bed_user(user, session):
    user_id = user.id
    answer = translate_text_for_user("Привет мой друг", session, user_id + 1)
    assert answer == "Привет мой друг"


@pytest.mark.translation
def test_detect_text_language():
    answer = _detect_text_language("Hello my friend")
    assert answer == "en"


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Hoghhflaff", "english", "spanish"),
                          ("Bdonfdjourr", "english", "french"),
                          ("Hafdllnnc", "english", "german"),
                          ])
@pytest.mark.translation
def test_translate_text_with_text_impossible_to_translate(
        text,
        target_lang,
        original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert answer == text


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("@Здравствуй#мой$друг!", "english", "russian"),
                          ("@Hola#mi$amigo!", "english", "spanish"),
                          ("@Bonjour#mon$ami!", "english", "french"),
                          ("@Hallo#mein$Freund!", "english", "german"),
                          ])
@pytest.mark.translation
def test_translate_text_with_symbols(text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert "@ Hello # my $ friend!" == answer


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Привет мой друг", "italian", "spanish"),
                          ("Hola mi amigo", "english", "russian"),
                          ("Bonjour, mon ami", "russian", "german"),
                          ("Ciao amico", "french", "german")
                          ])
@pytest.mark.translation
def test_translate_text_with_with_incorrect_lang(
        text,
        target_lang,
        original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert answer == text


@pytest.mark.translation
def test_get_user_language_for_bed_user(user, session):
    user_id = user.id + 1
    answer = _get_user_language(user_id, session=session)
    assert not answer


def test_get_user_language_for_bed_language(user, session):
    user.language_id = 3
    session.commit()
    with pytest.raises(HTTPException):
        answer = _get_user_language(user.id, session=session)
        assert answer.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
