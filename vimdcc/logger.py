import logging
import pathlib
from logging.handlers import TimedRotatingFileHandler

from .utils import cache


def file_handler():
    log_dir = pathlib.Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)

    fh = TimedRotatingFileHandler(
        filename=log_dir / 'vim.log',
        when='midnight',
        backupCount=7
    )

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
