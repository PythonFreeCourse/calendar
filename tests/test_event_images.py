from app.routers.event_images import attach_image_to_event,\
    generate_flare_link_from_lemmatized_word, get_image_name,\
    remove_non_alphabet_chars, search_token_in_related_words
import pytest


lemmatized_words = [
    ("ran",  r'..\static\event_flairs\ran.jpg'),
    ("food", r'..\static\event_flairs\food.jpg'),
    ("i",  r'..\static\event_flairs\i.jpg'),
    ("drank",  r'..\static\event_flairs\drank.jpg'),
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
    (r"backrub", r'..\static\event_flairs\massage.jpg'),
    (r"--MedicineS", r'..\static\event_flairs\pill.jpg'),
    (r"restaurants", r'..\static\event_flairs\food.jpg'),
    (r"pikachu", None),
    (r"Pokemon", r'..\static\event_flairs\pokemon.jpg'),
]


@pytest.mark.parametrize('token, link', tokens)
def test_search_token_in_related_words(token, link):
    assert search_token_in_related_words(token) == link


event_contents = [
    (r"Don't forget backrub and medicines!!!!", r'..\static\event_flairs\massage.jpg'),
    (r"Don't forget medicines and backrub!!!!", r'..\static\event_flairs\pill.jpg'),
    (r"It's important to drink", r'..\static\event_flairs\drank.jpg'),
    (r"call Jim about tennis on friday", r'..\static\event_flairs\tennis.jpg'),
    (r"have to check on pikachu", r'#'),
    (r"---~ new pokemon episode at 19:00 ~~!!", r'..\static\event_flairs\pokemon.jpg'),
]


@pytest.mark.parametrize('event_content, link', event_contents)
def test_attach_image_to_event(event_content, link):
    assert attach_image_to_event(event_content) == link
