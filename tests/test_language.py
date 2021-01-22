import pytest

import app.internal.languages as languages


class TestLanguage:
    LANGUAGE_TESTS = [
        ('en', 'test', True),
        ('he', 'בדיקה', True),
        ('de', 'test', False),  # defaults to English translation.
    ]

    @staticmethod
    def test_get_translations_dict():
        translations = languages.get_translations_dict()
        assert translations

    @staticmethod
    def test_get_translations_dicts():
        translations_dicts = languages.get_translations_dicts()
        assert translations_dicts

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid", LANGUAGE_TESTS)
    def test_get_translations_dicts_return_all_supported_languages(language_code, translation, is_valid):
        translations_dicts = languages.get_translations_dicts()
        assert (language_code in translations_dicts and is_valid) or (
                language_code not in translations_dicts and not is_valid)

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid", LANGUAGE_TESTS)
    def test_get_translations_dicts_valid_translations(language_code, translation, is_valid):
        if is_valid:
            assert languages.get_translations_dicts()[language_code]["test_word"] == translation

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid", LANGUAGE_TESTS)
    def test_update_translations_dict(language_code, translation, is_valid):
        languages.update_translations_dict("en")  # Verify test starts at English.
        languages.update_translations_dict(language_code)
        assert languages.get_translations_dict()["test_word"] == translation

    @staticmethod
    def test_get_display_language():
        # TODO: Waiting for user registration.
        #  Test: no user, user not logged in and user with non-english set.
        pass
