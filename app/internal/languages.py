import gettext
import os
from pathlib import Path
from typing import Iterator

from app import config
from app.dependencies import templates

LANGUAGE_DIR = "app/locales"
LANGUAGE_DIR_TEST = "../app/locales"
TRANSLATION_FILE = "base"


def set_ui_language(language: str = None) -> None:
    """Sets the gettext translations to a given language.

    If the language requested is not supported, the translations default
    to the value of config.WEBSITE_LANGUAGE.

    Args:
        language: Optional; A valid language code that follows RFC 1766.
            Defaults to None.
            See also the Language Code Identifier (LCID) Reference for a list of
            valid language codes.

    .. _RFC 1766:
        https://tools.ietf.org/html/rfc1766.html

    .. _Language Code Identifier (LCID) Reference:
        https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c # noqa: E501
    """

    # TODO: Connect when user registration is completed.
    # if not language:
    #     language = _get_display_language(user_id: int)

    language_dir = _get_language_directory()

    if language not in list(_get_supported_languages(language_dir)):
        language = config.WEBSITE_LANGUAGE

    translations = gettext.translation(
        TRANSLATION_FILE,
        localedir=language_dir,
        languages=[language],
    )
    translations.install()
    templates.env.install_gettext_translations(translations, newstyle=True)


# TODO: Waiting for user registration. Add doc.
# def _get_display_language(user_id: int) -> str:
#     # TODO: handle user language setting:
#     #  If user is logged in, get language setting.
#     #  If user is not logged in, get default site setting.
#
#     if db_user:
#         return db_user.language
#     return config.WEBSITE_LANGUAGE


def _get_language_directory() -> str:
    """Returns the language directory relative path."""
    language_dir = LANGUAGE_DIR
    if Path(LANGUAGE_DIR_TEST).is_dir():
        # If running from test, change dir path.
        language_dir = LANGUAGE_DIR_TEST
    return language_dir


def _get_supported_languages(
        language_dir: str = _get_language_directory()
) -> Iterator[str]:
    """Returns a generator of supported translation languages codes.

    Args:
        language_dir: Optional; The path of the language directory.
            Defaults to the return value of _get_language_directory().

    Returns:
        A generator expression of the supported translation languages codes.
    """

    paths = [Path(f.path) for f in os.scandir(language_dir) if f.is_dir()]
    return (language.name for language in paths)
