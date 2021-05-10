import os
import time
#import requests
import logging

from dotenv import load_dotenv
from kafka_uptime_monitor import constants, utils


class PingProducer(object):

    def __init__(self):
        # Load the producer's configuration from environment variables.
        load_dotenv()

        self._config = {
            # Integer parameters.
            **utils.load_from_env([
                constants.PING_INTERVAL_SECONDS,
                constants.LOG_LEVEL,
            ], converter=int),

            # String parameters.
            **utils.load_from_env([
                constants.PING_TARGET_WEBSITE_URL,
                constants.PING_CONTENT_REGEX,
                constants.LOG_FILENAME_BASE,
            ], converter=None)
        }

        # Set the log file name so that we know it's from a producer.
        self._config[constants.LOG_FILE_NAME] = f"{self._config[constants.LOG_FILENAME_BASE]}{constants.PRODUCER_LOGFILE_SUFFIX}"
        utils.configure_logger(self._config)


    def run(self):
        """
        Keep sending GET requests to the monitored website URL.
        """
        while True:
            #response = requests.get(
            #    self._config[constants.PING_TARGET_WEBSITE_URL]
            #)
            logging.debug(f"Producing off the URL {self._config[constants.PING_TARGET_WEBSITE_URL]}.")
            time.sleep(self._config[constants.PING_INTERVAL_SECONDS])
