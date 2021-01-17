from nltk.tokenize import word_tokenize
from typing import Optional
from word_forms.lemmatizer import lemmatize

import re


IMAGES_LINK_MAP = {
    'birthday': r'event_flairs\birthday.jpg',
    'coffee': r'event_flairs\coffee.jpg',
    'concert': r'event_flairs\concert.jpg',
    'cycle': r'event_flairs\cycling.jpg',
    'dentist': r'event_flairs\dentist.jpg',
    'food': r'event_flairs\food.jpg',
    'drank': r'event_flairs\drinks.png',
    'golf': r'event_flairs\golf.jpg',
    'graduate': r'event_flairs\graduation.jpg',
    'gym': r'event_flairs\gym.jpg',
    'haircut': r'event_flairs\haircut.jpg',
    'halloween': r'event_flairs\halloween.jpg',
    'hike': r'event_flairs\hiking.png',
    'kayak': r'event_flairs\kayaking.jpg',
    'music': r'event_flairs\music.jpg',
    'manicure': r'event_flairs\manicure.jpg',
    'massage': r'event_flairs\massage.jpg',
    'pill': r'event_flairs\pills.jpg',
    'pingpong': r'event_flairs\pingpong.jpg',
    'plan': r'event_flairs\plan.jpg',
    'pokemon': r'event_flairs\pokemon.jpg',
    'read': r'event_flairs\read.jpg',
    'repair': r'event_flairs\repair.png',
    'ran': r'event_flairs\running.jpg',
    'sail': r'event_flairs\sailing.jpg',
    'santa': r'event_flairs\santa.png',
    'ski': r'event_flairs\skiing.jpg',
    'soccer': r'event_flairs\soccer.jpg',
    'swam': r'event_flairs\swimming.png',
    'tennis': r'event_flairs\Tennis.png',
    'thanksgiving': r'event_flairs\thanksgiving.jpg',
    'wed': r'event_flairs\wedding.jpg',
    'christmas': r'event_flairs\xmas.jpg',
    'yoga': r'event_flairs\yoga.jpg',
}


IMAGES_RELATED_WORDS_MAP = {
    'birthday': ['birthday'],
    'coffee': ['coffee', 'coffees'],
    'concert': ['concert', 'gig', 'concerts', 'gigs'],
    'cycle': ['bicycle', 'cycling', 'bike', 'bicycles', 'bikes', 'Biking'],
    'dentist': ['dentist', 'dentistry', 'dental'],
    'food': ['dinner', 'dinners', 'restaurant', 'restaurants', 'Family meal', 'lunch', 'lunches', 'luncheon'],
    'drank': ['cocktail', 'drinks', 'cocktails'],
    'golf': ['golf'],
    'graduate': ['graduation'],
    'gym': ['gym', 'workout', 'workouts'],
    'haircut': ['haircut', 'hair'],
    'halloween': ['halloween', 'helloween', "hallowe'en", 'Allhalloween', "All Hallows' Eve", "All Saints' Eve"],
    'hike': ['hiking', 'hike', 'hikes'],
    'kayak': ['kayaking'],
    'music': ['piano', 'singing', 'music Class', 'choir practice', 'flute', 'orchestra', 'oboe', 'clarinet', 'saxophone', 'cornett', 'trumpet', 'contrabass', 'cello', 'trombone', 'tuba', 'music ensemble', 'string quartett', 'guitar lesson', 'classical music', 'choir'],
    'manicure': ['manicure', 'pedicure', 'manicures', 'pedicures'],
    'massage': ['massage', 'back rub', 'backrub', 'massages'],
    'pill': ['pills', 'medicines', 'medicine', 'drug', 'drugs'],
    'pingpong': ['ping pong', 'table tennis', 'ping-pong', 'pingpong'],
    'plan': ['plan week', 'plan quarter', 'plan day', 'plan vacation', 'week planning', 'vacation planning'],
    'pokemon': ['pokemon'],
    'read': ['reading', 'newspaper'],
    'repair': ['fridge repair', 'handyman', 'electrician', 'DIY'],
    'ran': ['jog', 'jogging', 'running', 'jogs', 'runs'],
    'sail': ['sail', 'sailing', 'boat cruise', 'sailboat'],
    'santa': ['Santa Claus', 'Father Christmas'],
    'ski': ['skiing', 'ski', 'skis', 'Snowboarding', 'snowshoeing', 'snow shoe', 'snow boarding'],
    'soccer': ['soccer'],
    'swam': ['swim', 'swimming', 'swims'],
    'tennis': ['tennis'],
    'thanksgiving': ['thanksgiving'],
    'wed': ['wedding', 'wedding eve', 'wedding-eve party', 'weddings'],
    'christmas': ['christmas', 'xmas', 'x-mas'],
    'yoga': ['yoga'],
}


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
        val (str): The value to search its key in IMAGES_RELATED_WORDS_MAP dictionary.

    Returns:
        str: The value's key in IMAGES_RELATED_WORDS_MAP dictionary..
    """
    for key, values in IMAGES_RELATED_WORDS_MAP.items():
         if remove_non_alphabet_chars(val).lower() in [remove_non_alphabet_chars(val).lower() for val in values]:
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
        return IMAGES_LINK_MAP.get(key)


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
            except:
                base_word = token
            link = IMAGES_LINK_MAP.get(base_word)
            if link:
                return link
            link = search_token_in_related_words(token)
            if link:
                return link
            link = '#'
    return link