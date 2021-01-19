import logging
from pathlib import Path, PurePath
import sys


class NoWitFolderFoundError(Exception):
    pass

log_file_path = r'log.log'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

LOG_FORMAT = "%(levelname)s  %(asctime)s - %(message)s"
formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


logger.debug('shimmi')
