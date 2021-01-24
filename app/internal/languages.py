import glob
import json
from pathlib import PureWindowsPath
from typing import Dict, Union

from app import config

LANGUAGE_FILES_PATH = "app/languages/*.json"
LANGUAGE_FILES_PATH_TEST = "../app/languages/*.json"

translation_words = {}


def get_translation_words() -> Dict[str, Union[str, Dict[str, str]]]:
    """Gets and returns the translation_words, which is a dictionary of
    the translated words in either the user's language setting,
    or the default app setting.

    Returns:
        dict[str, Union[str, Dict[str, str]]]: a dictionary of string keys and
        their translation as their values. The value can either be a string,
        or a nested dictionary for plural translations.
    """
    if translation_words:
        return translation_words
    # TODO: Waiting for user registration. Restore when done.
    # display_language = get_display_language(user_id)
    # populate_with_language(display_language)
    populate_with_language(config.WEBSITE_LANGUAGE)
    return translation_words


# TODO: Waiting for user registration. Add doc.
# def get_display_language(user_id: int) -> str:
#     # TODO: handle user language setting:
#     #  If user is logged in, get language setting.
#     #  If user is not logged in, get default site setting.
#
#     if db_user:
#         return db_user.language
#     return config.WEBSITE_LANGUAGE


def populate_with_language(display_language: str) -> None:
    """Updates the translation_words to the requested language.
    If the language code is not supported by the applications, the dictionary
    defaults to the config.WEBSITE_LANGUAGE setting.

    Args:
        display_language (str): a valid code that follows RFC 1766.
        See also the Language Code Identifier (LCID) Reference for a list of
        valid codes.

    .. _RFC 1766:
        https://tools.ietf.org/html/rfc1766.html

    .. _Language Code Identifier (LCID) Reference:
        https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c?redirectedfrom=MSDN # noqa
    """
    translation_words_all_languages = get_translations_words_all_languages()
    global translation_words
    if display_language in translation_words_all_languages:
        translation_words = translation_words_all_languages[display_language]
    else:
        translation_words = translation_words_all_languages[
            config.WEBSITE_LANGUAGE]


def get_translations_words_all_languages() -> \
        Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
    """Gets and returns a dictionary of nested language dictionaries from
     the language translation files.

    Returns:
        dict[str, Dict[str, Union[str, Dict[str, str]]]]: a dictionary of
        language codes as string keys, and nested dictionaries of translations
        as their values.
    """
    language_translations = {}
    language_files = (glob.glob(LANGUAGE_FILES_PATH)
                      or glob.glob(LANGUAGE_FILES_PATH_TEST))
    for language_file in language_files:
        language_code = PureWindowsPath(language_file).stem
        with open(language_file, 'r', encoding='utf8') as file:
            language_translations[language_code] = json.load(file)
    return language_translations
