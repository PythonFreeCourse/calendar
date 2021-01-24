import pytest

from app import config
import app.internal.languages as languages


class TestLanguage:
    LANGUAGE_TESTS = [
        ('en', 'test', True),
        ('he', 'בדיקה', True),
        ('de', 'test', False),  # defaults to English translation.
    ]

    @staticmethod
    def test_get_translation_words():
        translations = languages.get_translation_words()
        assert translations

    @staticmethod
    def test_get_translations_words_all_languages():
        translations_dicts = languages.get_translations_words_all_languages()
        assert translations_dicts

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_translations_words_all_languages_return_all_supported_languages(
            language_code, translation, is_valid):
        translations_dicts = languages.get_translations_words_all_languages()
        assert (language_code in translations_dicts and is_valid) or (
                language_code not in translations_dicts and not is_valid)

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_translations_words_all_languages_valid_translations(
            language_code, translation, is_valid):
        if is_valid:
            assert languages.get_translations_words_all_languages()[
                       language_code]["test_word"] == translation

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_populate_with_language(language_code, translation, is_valid):
        # Reset test to default language.
        languages.populate_with_language(config.WEBSITE_LANGUAGE)

        languages.populate_with_language(language_code)
        assert languages.get_translation_words()["test_word"] == translation

    @staticmethod
    def test_get_display_language():
        # TODO: Waiting for user registration.
        #  Test: no user, user not logged in and user with non-english set.
        pass
