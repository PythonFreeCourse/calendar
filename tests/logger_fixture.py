import logging

import pytest
from _pytest.logging import caplog as _caplog  # noqa: F401
from loguru import logger

from app import config
from app.internal.logger_customizer import LoggerCustomizer


@pytest.fixture(scope='module')
def logger_instance():
    _logger = LoggerCustomizer.make_logger(config.LOGGER, "logger")

    return _logger


@pytest.fixture(scope='module')
def logger_external_configuration():
    from pathlib import Path
    config_path = Path(__file__).parent
    config_path = config_path.absolute() / 'logging_config.json'
    _logger = LoggerCustomizer.make_logger(config_path, "logger1")

    return _logger


@pytest.fixture
def caplog(_caplog):  # noqa: F811
    class PropagateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)
