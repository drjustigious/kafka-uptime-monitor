import logging
import json

from kafka import KafkaConsumer
from dotenv import load_dotenv
from kafka_uptime_monitor import constants, utils


class PingConsumer(object):

    def __init__(self):
        """
        Load environment variables to configure the producer, set up logging
        and initialize a Kafka client.
        """
        # Load the producer's configuration from environment variables.
        load_dotenv()

        self._config = {
            # Integer parameters.
            **utils.load_from_env([
                constants.AGGREGATION_SAMPLE_COUNT,
                constants.LOG_LEVEL,
            ], converter=int),

            # String parameters.
            **utils.load_from_env([
                constants.KAFKA_TOPIC,
                constants.KAFKA_GROUP,
                constants.KAFKA_BOOTSTRAP_URL,
                constants.LOG_FILENAME_BASE,
            ], converter=None)
        }

        # Set the log file name so that we know it's from a producer.
        self._config[constants.LOG_FILE_NAME] = f"{self._config[constants.LOG_FILENAME_BASE]}{constants.PRODUCER_LOGFILE_SUFFIX}"
        utils.configure_logger(self._config)

        # Hold reference to just one producer client.
        self._kafka_consumer = self.configure_kafka_consumer(self._config)    


    def run(self):
        """
        Keep checking for messages on the Kafka cluster
        until somebody tells the process to hang up (e.g. Ctrl+C).
        """
        # Log the appropriate parameters to signal startup.
        startup_parameters = {
            key: self._config[key]
            for key in [
                constants.KAFKA_TOPIC,                
                constants.AGGREGATION_SAMPLE_COUNT,             
            ]
        }
        logging.warn(f"Consumer: Starting up. {json.dumps(startup_parameters, ensure_ascii=False)}")

        for message in self._kafka_consumer:
            logging.info(message.value)

        logging.warn(f"Consumer: Exiting.")


    def configure_kafka_consumer(self, config):
        consumer = KafkaConsumer(
            config[constants.KAFKA_TOPIC],
            bootstrap_servers=[config[constants.KAFKA_BOOTSTRAP_URL]],
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=config[constants.KAFKA_GROUP],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))      
        )
        return consumer