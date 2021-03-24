import gettext
import os
from pathlib import Path
from typing import Iterator

from app import config
from app.dependencies import LOCALES_PATH, templates

TRANSLATION_FILE = "base"


def set_ui_language(language: str = None) -> None:
    """Sets the gettext translations to a given language.

    If the language requested is not supported, the translations default
    to the value of config.WEBSITE_LANGUAGE.

    Args:
        language: Optional; A valid language code that follows RFC 1766.
            Defaults to None.
            See also the Language Code Identifier (LCID) Reference for a list
            of valid language codes.

    .. _RFC 1766:
        https://tools.ietf.org/html/rfc1766.html

    .. _Language Code Identifier (LCID) Reference:
        https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-lcid/a9eac961-e77d-41a6-90a5-ce1a8b0cdb9c # noqa: E501
    """

    # TODO: Connect when user registration is completed.
    # if not language:
    #     language = _get_display_language(user_id: int)

    try:
        if language not in set(_get_supported_languages()):
            language = config.WEBSITE_LANGUAGE
    except TypeError:
        language = config.WEBSITE_LANGUAGE

    translations = gettext.translation(
        TRANSLATION_FILE,
        localedir=LOCALES_PATH,
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


def _get_supported_languages() -> Iterator[str]:
    """Returns a generator of supported translation languages codes."""
    paths = (Path(f.path) for f in os.scandir(LOCALES_PATH) if f.is_dir())
    return (language.name for language in paths)
