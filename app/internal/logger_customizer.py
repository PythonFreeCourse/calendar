import json
import sys
from typing import Union

from pathlib import Path
from loguru import logger, _Logger as Logger


class LoggerConfigError(Exception):
    pass


class LoggerCustomizer:

    @classmethod
    def make_logger(cls, config: Union[Path, dict], logger_name: str) -> Logger:        
        """Creates a loguru logger from given configuration path or dict.

        Args:
            config (Union[Path, dict]): Path to logger configuration file or dictionary of configuration
            logger_name (str): Logger instance created from configuration

        Raises:
            LoggerConfigError: Error raised when the configuration is invalid

        Returns:
            Logger: Loguru logger instance
        """
        if isinstance(config, Path):
            config = cls.load_logging_config(config_path)
        else:
            config = config

        try:
            logging_config = config.get(logger_name)
            logs_path = logging_config.get('path')
            log_file_path = logging_config.get('filename')

            logger = cls.customize_logging(
                file_path=Path(logs_path) / Path(log_file_path),
                level=logging_config.get('level'),
                retention=logging_config.get('retention'),
                rotation=logging_config.get('rotation'),
                format=logging_config.get('format')
            )
        except (TypeError, ValueError) as err:
            raise LoggerConfigError(
                f"You have an issue with your logger configuration: {err!r}, fix it please")

        return logger

    @classmethod
    def customize_logging(cls,
                          file_path: Path,
                          level: str,
                          rotation: str,
                          retention: str,
                          format: str
                          ) -> Logger:
        """Used to customize the logger instance

        Args:
            file_path (Path): Path where the log file is located
            level (str): The level wanted to start logging from
            rotation (str): Every how long the logs would be rotated(creation of new file)            retention (str): [description]
            format (str): The logging format

        Returns:
            Logger: Instance of a logger mechanism
        """
        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )
        logger.add(
            str(file_path),
            rotation=rotation,
            retention=retention,
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=format
        )

        return logger

    @classmethod
    def load_logging_config(cls, config_path: Union[Path, dict]) -> dict:
        """Loads logging configuration from file or dict

        Args:
            config_path (Union[Path, dict]): Path to logging configuration file

        Returns:
            dict: Configuration parsed as dictionary
        """
        # config = None
        with open(config_path) as config_file:
            config = json.load(config_file)
        return config