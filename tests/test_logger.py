import logging

import pytest

from app.internal.logger_customizer import LoggerCustomizer, LoggerConfigError


class TestLogger:

    @staticmethod
    def test_log_debug(caplog, client_with_logger):
        with caplog.at_level(logging.DEBUG):
            client_with_logger.logger.debug('Is it debugging now?')
            assert 'Is it debugging now?' in caplog.text

    @staticmethod
    def test_log_info(caplog, client_with_logger):
        with caplog.at_level(logging.INFO):
            client_with_logger.logger.info('App started')
            assert 'App started' in caplog.text

    @staticmethod
    def test_log_error(caplog, client_with_logger):
        with caplog.at_level(logging.ERROR):
            client_with_logger.logger.error('Something bad happened!')
            assert 'Something bad happened!' in caplog.text

    @staticmethod
    def test_log_critical(caplog, client_with_logger):
        with caplog.at_level(logging.CRITICAL):
            client_with_logger.logger.critical("WE'RE DOOMED!")
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
