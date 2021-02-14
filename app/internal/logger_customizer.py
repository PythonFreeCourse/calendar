from pathlib import Path
import sys

from loguru import _Logger as Logger, logger


class LoggerConfigError(Exception):
    pass


class LoggerCustomizer:

    @classmethod
    def make_logger(cls, log_path: Path,
                    log_filename: str,
                    log_level: str,
                    log_rotation_interval: str,
                    log_retention_interval: str,
                    log_format: str) -> Logger:
        """Creates a logger from given configurations

        Args:
            log_path (Path): Path where the log file is located
            log_filename (str):

            log_level (str): The level we want to start logging from
            log_rotation_interval (str): Every how long the logs
                would be rotated
            log_retention_interval (str): Amount of time in words defining
                how long the log will be kept
            log_format (str): The logging format

        Raises:
            LoggerConfigError: Error raised when the configuration is invalid

        Returns:
            Logger: Loguru logger instance
        """
        try:
            logger = cls.customize_logging(
                file_path=Path(log_path) / Path(log_filename),
                level=log_level,
                retention=log_retention_interval,
                rotation=log_rotation_interval,
                format=log_format
            )
        except (TypeError, ValueError) as err:
            raise LoggerConfigError(
                f"You have an issue with the logger configuration: {err!r}, "
                "fix it please")

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
            rotation (str): Every how long the logs would be
                rotated(creation of new file)
            retention (str): Amount of time in words defining how
                long a log is kept
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
