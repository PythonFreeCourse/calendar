import pytest

from app import config
from app.routers.event_images import (attach_image_to_event,
                                      generate_flare_link_from_lemmatized_word,
                                      get_image_name,
                                      remove_non_alphabet_chars,
                                      search_token_in_related_words)

static = config.STATIC_ABS_PATH

lemmatized_words = [
    ("ran", f'{static}\\event_flairs\\ran.jpg'),
    ("food", f'{static}\\event_flairs\\food.jpg'),
    ("i", f'{static}\\event_flairs\\i.jpg'),
    ("drank", f'{static}\\event_flairs\\drank.jpg'),
]


@pytest.mark.parametrize('lemmatized, link', lemmatized_words)
def test_generate_flare_link_from_lemmatized_word(lemmatized, link):
    assert generate_flare_link_from_lemmatized_word(lemmatized) == link


contents = [
    (r"it's my birthday!", r"itsmybirthday"),
    (r"iT's   my birthday!!!", r"iTsmybirthday"),
    (r"its my birthday", r"itsmybirthday"),
    (r"it's-my-birthday!1990", r"itsmybirthday"),
]


@pytest.mark.parametrize('content, alphabet_only', contents)
def test_remove_non_alphabet_chars(content, alphabet_only):
    assert remove_non_alphabet_chars(content) == alphabet_only


values = [
    (r"backrub", r"massage"),
    (r"--MedicineS", r"pill"),
    (r"restaurants", r"food"),
    (r"pikachu", None),
    (r"Pokemon", r"pokemon"),
]


@pytest.mark.parametrize('related_word, key', values)
def test_get_image_name(related_word, key):
    assert get_image_name(related_word) == key


tokens = [
    (r"backrub", f'{static}\\event_flairs\\massage.jpg'),
    (r"--MedicineS", f'{static}\\event_flairs\\pill.jpg'),
    (r"restaurants", f'{static}\\event_flairs\\food.jpg'),
    (r"pikachu", None),
    (r"Pokemon", f'{static}\\event_flairs\\pokemon.jpg'),
]


@pytest.mark.parametrize('token, link', tokens)
def test_search_token_in_related_words(token, link):
    assert search_token_in_related_words(token) == link


event_contents = [
    (r"memo backrub and medicines!!", f'{static}\\event_flairs\\massage.jpg'),
    (r"Dont forget medicines & backrub!", f'{static}\\event_flairs\\pill.jpg'),
    (r"Its important to drink", f'{static}\\event_flairs\\drank.jpg'),
    (r"call Jim about tennis friday", f'{static}\\event_flairs\\tennis.jpg'),
    (r"have to check on pikachu", r'#'),
    (r"-~new pokemon episode 19:00~!", f'{static}\\event_flairs\\pokemon.jpg'),
]


@pytest.mark.parametrize('event_content, link', event_contents)
def test_attach_image_to_event(event_content, link):
    assert attach_image_to_event(event_content) == link
