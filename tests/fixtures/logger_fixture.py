import logging

from _pytest.logging import caplog as _caplog  # noqa: F401
from loguru import logger
import pytest

from app import config
from app.internal.logger_customizer import LoggerCustomizer


@pytest.fixture(scope='module')
def logger_instance():
    _logger = LoggerCustomizer.make_logger(config.LOG_PATH,
                                           config.LOG_FILENAME,
                                           config.LOG_LEVEL,
                                           config.LOG_ROTATION_INTERVAL,
                                           config.LOG_RETENTION_INTERVAL,
                                           config.LOG_FORMAT)

    return _logger


@pytest.fixture
def caplog(_caplog):  # noqa: F811
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)
