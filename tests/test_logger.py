import logging

import pytest

from app.internal.logger_customizer import LoggerCustomizer, LoggerConfigError


class TestLogger:
    @staticmethod
    def test_configuration_file(caplog, logger_external_configuration):
        with caplog.at_level(logging.ERROR):
            logger_external_configuration.error('Testing configuration ERROR')
            assert 'Testing configuration' in caplog.text

    @staticmethod
    def test_log_debug(caplog, logger_instance):
        with caplog.at_level(logging.DEBUG):
            logger_instance.debug('Is it debugging now?')
            assert 'Is it debugging now?' in caplog.text

    @staticmethod
    def test_log_info(caplog, logger_instance):
        with caplog.at_level(logging.INFO):
            logger_instance.info('App started')
            assert 'App started' in caplog.text

    @staticmethod
    def test_log_error(caplog, logger_instance):
        with caplog.at_level(logging.ERROR):
            logger_instance.error('Something bad happened!')
            assert 'Something bad happened!' in caplog.text

    @staticmethod
    def test_log_critical(caplog, logger_instance):
        with caplog.at_level(logging.CRITICAL):
            logger_instance.critical("WE'RE DOOMED!")
            assert "WE'RE DOOMED!" in caplog.text

    @staticmethod
    def test_bad_configuration():
        bad_config = {
            "logger": {
                "path": "./var/log",
                "filename": "calendar.log",
                "level": "eror",
                "rotation": "20 days",
                "retention": "1 month",
                "format": ("<level>{level: <8}</level> "
                           "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
                           "- <cyan>{name}</cyan>:<cyan>{function}</cyan>"
                           " - <level>{message}</level>")
            }
        }
        with pytest.raises(LoggerConfigError):
            LoggerCustomizer.make_logger(bad_config, 'logger')
