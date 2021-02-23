from pathlib import Path

import pytest

from app.dependencies import templates
from app.internal import languages


class TestLanguage:
    # Empty, invalid, or valid, but unsupported language codes,
    # (currently 'en' and 'he') are set to the default language setting
    # at config.WEBSITE_LANGUAGE, which is currently set to 'en' (English).
    LANGUAGE_TESTS = [
        ('en', 'test python translation', True),
        ('he', 'בדיקת תרגום בפייתון', True),
        (None, 'test python translation', False),
        ('', 'test python translation', False),
        ('de', 'test python translation', False),
        (["en"], 'test python translation', False),
        (3, 'test python translation', False),
    ]

    NUMBER_OF_LANGUAGES = 2

    @staticmethod
    @pytest.mark.parametrize(
        "language_code, translation, is_valid", LANGUAGE_TESTS)
    def test_gettext_python(language_code, translation, is_valid):
        languages.set_ui_language(language_code)

        # i18n: String used in testing. Do not change.
        gettext_translation = _("test python translation")
        assert ((is_valid and gettext_translation == translation)
                or (not is_valid and gettext_translation == translation))

    @staticmethod
    @pytest.mark.parametrize(
        "language_code, translation, is_valid", LANGUAGE_TESTS)
    def test_gettext_html(language_code, translation, is_valid):
        languages.set_ui_language(language_code)

        template = templates.env.from_string(
            '{{ gettext("test python translation") }}')
        text = template.render()
        assert ((is_valid and translation in text)
                or (not is_valid and translation in text))

    @staticmethod
    def test_get_supported_languages():
        number_of_languages = len(list(languages._get_supported_languages()))
        assert number_of_languages == TestLanguage.NUMBER_OF_LANGUAGES

    @staticmethod
    def test_get_language_directory():
        pytest.MonkeyPatch().setattr(Path, 'is_dir', lambda x: True)
        assert languages._get_language_directory()

    @staticmethod
    def test_get_display_language():
        # TODO: Waiting for user registration.
        #  Test: no user, user not logged in and user with non-english set.
        pass
