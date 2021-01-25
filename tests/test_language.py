import pytest

import app.internal.languages as languages


class TestLanguage:
    LANGUAGE_TESTS = [
        ('en', 'test', True),
        ('he', 'בדיקה', True),
        ('de', 'test', False),  # defaults to English translation.
    ]

    @staticmethod
    def test_get_translation_words():
        assert languages.get_translation_words()

    @staticmethod
    def test_get_translation_words_all_languages():
        assert languages._get_translation_words_all_languages()

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_translation_words_all_languages_return_all_supported_languages(
            language_code, translation, is_valid):
        all_translations = languages._get_translation_words_all_languages()
        assert ((language_code in all_translations and is_valid)
                or (language_code not in all_translations and not is_valid))

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_translation_words_all_languages_valid_translations(
            language_code, translation, is_valid):
        if is_valid:
            assert languages._get_translation_words_all_languages()[
                       language_code]["test_word"] == translation

    @staticmethod
    @pytest.mark.parametrize("language_code, translation, is_valid",
                             LANGUAGE_TESTS)
    def test_populate_with_language(language_code, translation, is_valid):
        translations = languages._populate_with_language(language_code)
        assert translations["test_word"] == translation

    @staticmethod
    def test_get_display_language():
        # TODO: Waiting for user registration.
        #  Test: no user, user not logged in and user with non-english set.
        pass
