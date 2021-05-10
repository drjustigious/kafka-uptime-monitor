import os

from dotenv import load_dotenv
from kafka_uptime_monitor import constants


class PingConsumer(object):

    def run(self):
        """
        Start the ping consumer.

        Configuration will be loaded from environment variables.
        """
        load_dotenv()
        print("Aggregation sample count:", os.getenv(constants.AGGREGATION_SAMPLE_COUNT))