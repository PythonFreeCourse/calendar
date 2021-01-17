from nltk.tokenize import word_tokenize
from typing import Optional
from word_forms.lemmatizer import lemmatize

import re


FLAIRS_EXTENSION = '.jpg'
FLAIRS_REL_PATH = r'event_flairs'
IMAGES_RELATED_WORDS_MAP = {
    'birthday': ['birthday'],
    'coffee': ['coffee', 'coffees'],
    'concert': ['concert', 'gig', 'concerts', 'gigs'],
    'cycle': ['bicycle', 'cycling', 'bike', 'bicycles', 'bikes', 'Biking'],
    'dentist': ['dentist', 'dentistry', 'dental'],
    'food': ['dinner', 'dinners', 'restaurant', 'restaurants',
             'Family meal', 'lunch', 'lunches', 'luncheon'],
    'drank': ['cocktail', 'drinks', 'cocktails'],
    'golf': ['golf'],
    'graduate': ['graduation'],
    'gym': ['gym', 'workout', 'workouts'],
    'haircut': ['haircut', 'hair'],
    'halloween': ['halloween', 'helloween', "hallowe'en",
                  'Allhalloween', "All Hallows' Eve", "All Saints' Eve"],
    'hike': ['hiking', 'hike', 'hikes'],
    'kayak': ['kayaking'],
    'music': ['piano', 'singing', 'music Class', 'choir practice',
              'flute', 'orchestra', 'oboe', 'clarinet', 'saxophone',
              'cornett', 'trumpet', 'contrabass', 'cello', 'trombone',
              'tuba', 'music ensemble', 'string quartett',
              'guitar lesson', 'classical music', 'choir'],
    'manicure': ['manicure', 'pedicure', 'manicures', 'pedicures'],
    'massage': ['massage', 'back rub', 'backrub', 'massages'],
    'pill': ['pills', 'medicines', 'medicine', 'drug', 'drugs'],
    'pingpong': ['ping pong', 'table tennis', 'ping-pong', 'pingpong'],
    'plan': ['plan week', 'plan quarter', 'plan day', 'plan vacation',
             'week planning', 'vacation planning'],
    'pokemon': ['pokemon'],
    'read': ['reading', 'newspaper'],
    'repair': ['fridge repair', 'handyman', 'electrician', 'DIY'],
    'ran': ['jog', 'jogging', 'running', 'jogs', 'runs'],
    'sail': ['sail', 'sailing', 'boat cruise', 'sailboat'],
    'santa': ['Santa Claus', 'Father Christmas'],
    'ski': ['skiing', 'ski', 'skis', 'Snowboarding', 'snowshoeing',
            'snow shoe', 'snow boarding'],
    'soccer': ['soccer'],
    'swam': ['swim', 'swimming', 'swims'],
    'tennis': ['tennis'],
    'thanksgiving': ['thanksgiving'],
    'wed': ['wedding', 'wedding eve', 'wedding-eve party', 'weddings'],
    'christmas': ['christmas', 'xmas', 'x-mas'],
    'yoga': ['yoga'],
}


def generate_flare_link_from_lemmatized_word(lemmatized_word: str) -> str:
    """Generate a link to a flair by a given lemmatized word.

    Args:
        lemmatized_word (str): The lemmatized word.

    Returns:
        str: The suitable link.
    """
    return f'{FLAIRS_REL_PATH}\{lemmatized_word}{FLAIRS_EXTENSION}'


def remove_non_alphabet_chars(s: str) -> str:
    """Remove non-alphabet chars from a given string

    Args:
        s (str): The string to remove the non-alphabet chars from.

    Returns:
        str: The string after the removal.
    """
    regex = re.compile('[^a-zA-Z]')
    return regex.sub('', s)


def get_key(val: str) -> Optional[str]:
    """Search the key of a given value in IMAGES_RELATED_WORDS_MAP dictionary.

    Args:
        val (str): The value to search its key.

    Returns:
        str: The value's key in IMAGES_RELATED_WORDS_MAP dictionary..
    """
    shrunken = remove_non_alphabet_chars(val).lower()
    for key, values in IMAGES_RELATED_WORDS_MAP.items():
        shrunken_list = [remove_non_alphabet_chars(v).lower() for v in values]
        if shrunken in shrunken_list:
            return key


def search_token_in_related_words(token: str) -> Optional[str]:
    """Search a token in IMAGES_RELATED_WORDS_MAP dictionary.

    Args:
        token (str): The token to search.

    Returns:
        str: The link to the suitable image of the given token.
    """
    key = get_key(token)
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
        if re.match(r'\w', token):
            try:
                base_word = lemmatize(remove_non_alphabet_chars(token).lower())
            except ValueError:
                base_word = token
            if base_word in IMAGES_RELATED_WORDS_MAP.keys():
                return generate_flare_link_from_lemmatized_word(base_word)
            link = search_token_in_related_words(token)
            if link:
                return link
            link = '#'
    return link

print(attach_image_to_event("Don't forget backrub and medicines!!!!"))