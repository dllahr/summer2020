import logging
import logging.handlers

__author__ = "David Lahr"
__email__ = "dlahr@broadinstitute.org"

LOGGER_NAME = "FHT_logger"

_LOG_FORMAT = "%(levelname)s %(asctime)s %(module)s %(funcName)s %(message)s"
_LOG_FILE_MAX_BYTES = 10000000
_LOG_FILE_BACKUP_COUNT = 5


def setup(verbose=False, log_file=None):
    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT))
    logger.addHandler(consoleHandler)

    if log_file is not None:
        fileHandler = logging.handlers.RotatingFileHandler(
            log_file, _LOG_FILE_MAX_BYTES, _LOG_FILE_BACKUP_COUNT)
        fileHandler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT))
        logger.addHandler(fileHandler)
