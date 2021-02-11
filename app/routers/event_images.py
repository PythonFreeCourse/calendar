from functools import lru_cache
import re
from typing import Optional

from nltk.tokenize import word_tokenize
from word_forms.lemmatizer import lemmatize

from app import config

FLAIRS_EXTENSION = '.jpg'
FLAIRS_REL_PATH = f'{config.STATIC_ABS_PATH}\\event_flairs'
IMAGES_RELATED_WORDS_MAP = {
    'birthday': 'birthday',
    'coffee': 'coffee',
    'coffees': 'coffee',
    'concert': 'concert',
    'gig': 'concert',
    'concerts': 'concert',
    'gigs': 'concert',
    'bicycle': 'cycle',
    'cycling': 'cycle',
    'bike': 'cycle',
    'bicycles': 'cycle',
    'bikes': 'cycle',
    'biking': 'cycle',
    'dentist': 'dentist',
    'dentistry': 'dentist',
    'dental': 'dentist',
    'dinner': 'food',
    'dinners': 'food',
    'restaurant': 'food',
    'restaurants': 'food',
    'family meal': 'food',
    'lunch': 'food',
    'lunches': 'food',
    'luncheon': 'food',
    'cocktail': 'drank',
    'drinks': 'drank',
    'cocktails': 'drank',
    'golf': 'golf',
    'graduation': 'graduate',
    'gym': 'gym',
    'workout': 'gym',
    'workouts': 'gym',
    'haircut': 'haircut',
    'hair': 'haircut',
    'halloween': 'halloween',
    'helloween': 'halloween',
    "hallowe'en": 'halloween',
    'allhalloween': 'halloween',
    "all hallows' eve": 'halloween',
    "all saints' Eve": 'halloween',
    'hiking': 'hike',
    'hike': 'hike',
    'hikes': 'hike',
    'kayaking': 'kayak',
    'piano': 'music',
    'singing': 'music',
    'music class': 'music',
    'choir practice': 'music',
    'flute': 'music',
    'orchestra': 'music',
    'oboe': 'music',
    'clarinet': 'music',
    'saxophone': 'music',
    'cornett': 'music',
    'trumpet': 'music',
    'contrabass': 'music',
    'cello': 'music',
    'trombone': 'music',
    'tuba': 'music',
    'music ensemble': 'music',
    'string quartett': 'music',
    'guitar lesson': 'music',
    'classical music': 'music',
    'choir': 'music',
    'manicure': 'manicure',
    'pedicure': 'manicure',
    'manicures': 'manicure',
    'pedicures': 'manicure',
    'massage': 'massage',
    'back rub': 'massage',
    'backrub': 'massage',
    'massages': 'massage',
    'pills': 'pill',
    'medicines': 'pill',
    'medicine': 'pill',
    'drug': 'pill',
    'drugs': 'pill',
    'ping pong': 'pingpong',
    'table tennis': 'pingpong',
    'ping-pong': 'pingpong',
    'pingpong': 'pingpong',
    'plan week': 'plan',
    'plan quarter': 'plan',
    'plan day': 'plan',
    'plan vacation': 'plan',
    'week planning': 'plan',
    'vacation planning': 'plan',
    'pokemon': 'pokemon',
    'reading': 'read',
    'newspaper': 'read',
    'fridge repair': 'repair',
    'handyman': 'repair',
    'electrician': 'repair',
    'diy': 'repair',
    'jog': 'ran',
    'jogging': 'ran',
    'running': 'ran',
    'jogs': 'ran',
    'runs': 'ran',
    'sail': 'sail',
    'sailing': 'sail',
    'boat cruise': 'sail',
    'sailboat': 'sail',
    'santa claus': 'santa',
    'father christmas': 'santa',
    'skiing': 'ski',
    'ski': 'ski',
    'skis': 'ski',
    'snowboarding': 'ski',
    'snowshoeing': 'ski',
    'snow shoe': 'ski',
    'snow boarding': 'ski',
    'soccer': 'soccer',
    'swim': 'swam',
    'swimming': 'swam',
    'swims': 'swam',
    'tennis': 'tennis',
    'thanksgiving': 'thanksgiving',
    'wedding': 'wed',
    'wedding eve': 'wed',
    'wedding-eve party': 'wed',
    'weddings': 'wed',
    'christmas': 'christmas',
    'xmas': 'christmas',
    'x-mas': 'christmas',
    'yoga': 'yoga',
}


def generate_flare_link_from_lemmatized_word(lemmatized_word: str) -> str:
    """Generate a link to a flair by a given lemmatized word.

    Args:
        lemmatized_word (str): The lemmatized word.

    Returns:
        str: The suitable link.
    """
    return f'{FLAIRS_REL_PATH}\\{lemmatized_word}{FLAIRS_EXTENSION}'


def remove_non_alphabet_chars(text: str) -> str:
    """Remove non-alphabet chars from a given string

    Args:
        text (str): The string to remove the non-alphabet chars from.

    Returns:
        str: The string after the removal.
    """
    regex = re.compile('[^a-zA-Z]')
    return regex.sub('', text)


def get_image_name(related_word: str) -> Optional[str]:
    """Search the key of a given value in IMAGES_RELATED_WORDS_MAP dictionary.

    Args:
        related_word (str): The value to search its key.

    Returns:
        str: The value's key in IMAGES_RELATED_WORDS_MAP dictionary.
    """
    shrunken = remove_non_alphabet_chars(related_word).lower()
    return IMAGES_RELATED_WORDS_MAP.get(shrunken)


@lru_cache(maxsize=32)
def search_token_in_related_words(token: str) -> Optional[str]:
    """Search a token in IMAGES_RELATED_WORDS_MAP dictionary.

    Args:
        token (str): The token to search.

    Returns:
        str: The link to the suitable image of the given token.
    """
    key = get_image_name(token)
    if key:
        return generate_flare_link_from_lemmatized_word(key)


def attach_image_to_event(event_content: str) -> str:
    """Get a link to the suitable image of a given token content.

    Args:
        event_content (str): The event content.

    Returns:
        str: The link to the suitable image of a given token content.
    """
    event_tokens = word_tokenize(event_content)
    for token in event_tokens:
        if token.isalnum():
            try:
                base_word = lemmatize(remove_non_alphabet_chars(token).lower())
            except ValueError:
                base_word = token
            if base_word in IMAGES_RELATED_WORDS_MAP.values():
                return generate_flare_link_from_lemmatized_word(base_word)
            link = search_token_in_related_words(token)
            if link:
                return link
            link = '#'
    return link
