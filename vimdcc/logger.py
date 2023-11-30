import logging
from typing import Dict

from .utils import cache

# TODO: Add log rotation


def file_handler():
    fh = logging.FileHandler('logs.log', 'w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    return fh


def stream_handler():
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    return sh


@cache
def get_logger() -> logging.Logger:
    logger = logging.getLogger('vim')
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler())
    logger.addHandler(file_handler())
    return logger


LOGGER = get_logger()
