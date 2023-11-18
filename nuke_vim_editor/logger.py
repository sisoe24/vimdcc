import logging


def file_handler():
    fh = logging.FileHandler('logs.log', 'w')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    return fh


def stream_handler():
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    return sh


_LOGGERS = {}


def get_logger() -> logging.Logger:
    if not _LOGGERS.get('vim'):
        logger = logging.getLogger('vim')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler())
        logger.addHandler(file_handler())
        _LOGGERS['vim'] = logger

    return _LOGGERS['vim']


LOGGER = get_logger()
