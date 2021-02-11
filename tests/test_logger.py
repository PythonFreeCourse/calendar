import logging

import pytest

from app import config
from app.internal.logger_customizer import LoggerConfigError, LoggerCustomizer


class TestLogger:
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
        with pytest.raises(LoggerConfigError):
            LoggerCustomizer.make_logger(config.LOG_PATH,
                                         config.LOG_FILENAME,
                                         'eror',
                                         config.LOG_ROTATION_INTERVAL,
                                         config.LOG_RETENTION_INTERVAL,
                                         config.LOG_FORMAT)
