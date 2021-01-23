import json
import pathlib
from typing import Dict, Union

from app import config

LANGUAGE_DIR_PATH = "../app/languages"

translations_dict = {}


def get_translations_dict() -> Dict[str, Union[str, Dict[str, str]]]:
    """Gets and returns the translations_dict, which is a dictionary of
    the translated words in either the user's language setting,
    or the default app setting.

    Returns:
        dict[str, Union[str, Dict[str, str]]]: a dictionary of string keys and
        their translation as their values. The value can either be a string,
        or a nested dictionary for plural translations.
    """
    if translations_dict:
        return translations_dict
    # TODO: Waiting for user registration. Restore when done.
    # display_language = get_display_language(user_id)
    # update_translations_dict(display_language)
    update_translations_dict(config.WEBSITE_LANGUAGE)
    return translations_dict


# TODO: Waiting for user registration. Add doc.
# def get_display_language(user_id: int) -> str:
#     # TODO: handle user language setting:
#     #  If user is logged in, get language setting.
#     #  If user is not logged in, get default site setting.
#
#     if db_user:
#         return db_user.language
#     return APP_LANGUAGE


def update_translations_dict(display_language: str) -> None:
    """Updates the translations_dict to the requested language.
    If the language code is not supported by the applications, the dictionary
    defaults to the APP_LANGUAGE setting.

    Args:
        display_language (str): a valid code that follows RFC 1766.
        See also the Language Code Identifier (LCID) Reference for a list of
        valid codes.

    .. _RFC 1766:
        https://tools.ietf.org/html/rfc1766.html

    .. _Language Code Identifier (LCID) Reference:
        https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c?redirectedfrom=MSDN # noqa
    """
    translations_dicts = get_translations_dicts()
    global translations_dict
    if display_language in translations_dicts:
        translations_dict = translations_dicts[display_language]
    else:
        translations_dict = translations_dicts[config.WEBSITE_LANGUAGE]


def get_translations_dicts() -> \
        Dict[str, Dict[str, Union[str, Dict[str, str]]]]:
    """Gets and returns a dictionary of nested language dictionaries from
     the language translation files.

    Returns:
        dict[str, Dict[str, Union[str, Dict[str, str]]]]: a dictionary of
        language codes as string keys, and nested dictionaries of translations
        as their values.
    """
    language_translations = {}
    for language_file in pathlib.Path(LANGUAGE_DIR_PATH).glob("*.json"):
        language_code = language_file.stem
        with open(language_file, 'r', encoding='utf8') as file:
            language_translations[language_code] = json.load(file)
    return language_translations
