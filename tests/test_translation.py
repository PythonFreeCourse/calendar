import pytest
from iso639 import languages
from textblob import TextBlob

from app.internal.translation import \
    translate_text, \
    translate_text_for_user, \
    _get_user_language, \
    _lang_full_to_short, \
    _detect_text_language


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Привет мой друг", "english", "russian"),
                          ("Hola mi amigo", "english", "spanish"),
                          ("Bonjour, mon ami", "english", "french"),
                          ("Hallo, mein Freund", "english", "german"),
                          ])
def test_translate_text_with_original_lang(text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert "Hello my friend" == answer
    assert TextBlob(text).detect_language() == languages.get(name=original_lang.capitalize()).alpha2
    assert TextBlob(answer).detect_language() == languages.get(name=target_lang.capitalize()).alpha2


@pytest.mark.parametrize("text, target_lang",
                         [("Привет мой друг", "english"),
                          ("Bonjour, mon ami", "english"),
                          ("Hallo, mein Freund", "english"),
                          ])
def test_translate_text_without_original_lang(text, target_lang):
    answer = translate_text(text, target_lang)
    assert "Hello my friend" == answer
    assert TextBlob(answer).detect_language() == languages.get(name=target_lang.capitalize()).alpha2


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Привет мой друг", "russian", "russian"),
                          ("Hola mi amigo", "spanish", "spanish"),
                          ("Bonjour, mon ami", "french", "french"),
                          ("Hallo, mein Freund", "german", "german"),
                          ("Ciao amico", "italian", "italian")
                          ])
def test_translate_text_with_same_original_target_lang_with_original_lang(text, target_lang, original_lang):
    answer = translate_text(text, target_lang, original_lang)
    assert answer == text


@pytest.mark.parametrize("text, target_lang",
                         [("Привет мой друг", "russian"),
                          ("Hola mi amigo", "spanish"),
                          ("Bonjour, mon ami", "french"),
                          ("Hallo, mein Freund", "german"),
                          ("Ciao amico", "italian")
                          ])
def test_translate_text_with_same_original_target_lang_without_original_lang(text, target_lang):
    answer = translate_text(text, target_lang)
    assert answer == text


def test_translate_text_without_text_with_original_target_lang():
    answer = translate_text("", "english", "russian")
    assert answer == "No text to translate"


def test_translate_text_without_text_without_original_lang():
    answer = translate_text("", "english")
    assert answer == "No text to translate"


def test_lang_short_to_full():
    answer = _lang_full_to_short("english")
    assert answer == "en"


def test_get_user_language(user, session):
    user_id = user.id
    answer = _get_user_language(user_id, session=session)
    assert user_id == 1
    assert answer.lower() == "english"


@pytest.mark.parametrize("text", ["Привет мой друг",
                                  "Bonjour, mon ami",
                                  "Hello my friend"]
                         )
def test_translate_text_for_user(text, user, session):
    user_id = user.id
    answer = translate_text_for_user(text, session, user_id)
    assert answer == "Hello my friend"


def test_detect_text_language():
    answer = _detect_text_language("Hello my friend")
    assert answer == "en"


@pytest.mark.parametrize("text, target_lang, original_lang",
                         [("Hoghhflaff", "english", "spanish"),
                          ("Bdonfdjourr", "english", "french"),
                          ("Hafdllnnc", "english", "german"),
                          ])
def test_translate_text_with_text_impossible_to_translate(text, target_lang, original_lang):
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
