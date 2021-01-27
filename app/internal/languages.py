import gettext
import os
from pathlib import Path
from typing import List

from app import config
from app.dependencies import templates

LANGUAGE_DIR = "app/locales"
LANGUAGE_DIR_TEST = "../app/locales"
TRANSLATION_FILE = "base"


def setup_ui_language() -> None:
    """Set the jinja2 environment on startup to support the i18n
    and call set_ui_language() to setup an initial language for translations.
    """
    templates.env.add_extension('jinja2.ext.i18n')
    set_ui_language()


def set_ui_language(language: str = None) -> None:
    """Set the gettext translations to a given language.
    If the language requested is not supported, the translations default
    to the value of config.WEBSITE_LANGUAGE.

    Args:
        language (str, optional): a valid language code that follows RFC 1766.
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

    if language not in _get_supported_languages():
        language = config.WEBSITE_LANGUAGE

    if Path(LANGUAGE_DIR).is_dir():
        language_dir = LANGUAGE_DIR
    else:
        language_dir = LANGUAGE_DIR_TEST

    translations = gettext.translation(TRANSLATION_FILE,
                                       localedir=language_dir,
                                       languages=[language])
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


def _get_supported_languages() -> List[str]:
    """Get and return a list of supported translation languages codes.

    Returns:
        List[str]: a list of supported translation languages codes.
    """
    try:
        language_dir = os.scandir(LANGUAGE_DIR)
    except FileNotFoundError:
        language_dir = os.scandir(LANGUAGE_DIR_TEST)
    return [language.name for language in
            [Path(f.path) for f in language_dir if f.is_dir()]]
