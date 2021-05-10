import logging
import logging.handlers
import os
import sys

from typing import Any
from kafka_uptime_monitor import constants


def configure_logger(config: dict):
    """
    Set up a rotating file handler. The log file name and logging level
    are determined from the given config dictionary.
    """

    rotating_file_handler = logging.handlers.RotatingFileHandler(
        filename=config[constants.LOG_FILE_NAME],
        mode='a',
        maxBytes=20*1024*1024,
        backupCount=2,
        encoding='utf-8',
        delay=0
    )

    console_logging_handler = logging.StreamHandler(
        stream=sys.stdout
    )

    logging.basicConfig(
        level=config[constants.LOG_LEVEL],
        format=constants.LOGGING_FORMAT,
        datefmt=constants.DATE_FORMAT,
        handlers=[
            rotating_file_handler,
            console_logging_handler
        ]
    )


def load_from_env(keys: list, converter: callable = None) -> dict:
    """
    Given a list of string keys, try to read the corresponding values
    from the environment variables. Convert the found values by
    passing them through 'converter' and return the results as a dict.
    """
    if converter is None:
        converter = lambda x: x

    converted_config = {
        key: converter(os.getenv(key))
        for key in keys
    }

    return converted_config