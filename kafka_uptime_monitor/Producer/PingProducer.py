import time
from kafka.consumer import group
import requests
import logging
import datetime
import re
import json

from dataclasses import dataclass
from dotenv import load_dotenv
from kafka import KafkaProducer
from kafka_uptime_monitor import constants, utils


@dataclass
class PingObservation:
    """
    A representation of one pinging attempt. Note that all properties
    except observation_time can also be None.
    """
    observation_time: datetime.datetime
    response_time: datetime.timedelta
    response_status: int
    regex_matched: bool


    def render_into_dict(self) -> dict:
        """
        Format the observation into a dictionary that can be serialized to JSON.
        """
        data = {
            constants.OBSERVATION_TIME: self.observation_time.strftime(constants.DATE_FORMAT),
            constants.RESPONSE_TIME: self.response_time.microseconds/1000 if self.response_time is not None else None,
            constants.RESPONSE_STATUS: self.response_status if self.response_status is not None else None,
            constants.REGEX_MATCHED: self.regex_matched if self.regex_matched is not None else None
        }
        return data



class PingProducer(object):

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
                constants.PING_INTERVAL_SECONDS,
                constants.PING_TIMEOUT_SECONDS,
                constants.LOG_LEVEL,
            ], converter=int),

            # String parameters.
            **utils.load_from_env([
                constants.PING_TARGET_WEBSITE_URL,
                constants.PING_REGEX_PATTERN,
                constants.LOG_FILENAME_BASE,
                constants.KAFKA_TOPIC,
                constants.KAFKA_BOOTSTRAP_URL
            ], converter=None)
        }

        # Set the log file name so that we know it's from a producer.
        self._config[constants.LOG_FILE_NAME] = f"{self._config[constants.LOG_FILENAME_BASE]}{constants.PRODUCER_LOGFILE_SUFFIX}"
        utils.configure_logger(self._config)

        # Hold reference to just one producer client.
        self._kafka_producer = self.configure_kafka_producer(self._config)


    def run(self):
        """
        Keep sending GET requests to the monitored website URL
        until somebody tells the process to hang up (e.g. Ctrl+C).
        """
        # Log the appropriate parameters to signal startup.
        startup_parameters = {
            key: self._config[key]
            for key in [
                constants.KAFKA_TOPIC,
                constants.PING_TARGET_WEBSITE_URL,
                constants.PING_REGEX_PATTERN,
                constants.PING_INTERVAL_SECONDS,
                constants.PING_TIMEOUT_SECONDS,                
            ]
        }
        logging.warn(f"Producer: Starting up. {json.dumps(startup_parameters, ensure_ascii=False)}")

        while True:
            response = self.send_ping()
            observation = self.collect_results(response)
            self.publish_observation(observation)
            time.sleep(self._config[constants.PING_INTERVAL_SECONDS])

        logging.warn("Producer: Exiting.")


    def configure_kafka_producer(self, config: dict) -> KafkaProducer:
        producer = KafkaProducer(
            bootstrap_servers=config[constants.KAFKA_BOOTSTRAP_URL],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        return producer


    def publish_observation(self, observation: PingObservation):
        """
        Push the given ping observation into the configured Kafka cluster.
        """
        observation_as_dict = observation.render_into_dict()
        logging.debug(f"Producer: Publishing the following observation.\n{observation_as_dict}")

        self._kafka_producer.send(
            self._config[constants.KAFKA_TOPIC],
            observation_as_dict
        )


    def send_ping(self) -> requests.Response:
        """
        Send a HTTP GET request to the configured URL and return the response.
        """
        try:
            logging.debug(f"Producer: Pinging {self._config[constants.PING_TARGET_WEBSITE_URL]}.")
            response = requests.get(
                self._config[constants.PING_TARGET_WEBSITE_URL],
                timeout=self._config[constants.PING_TIMEOUT_SECONDS]
            )
        except requests.Timeout:
            logging.debug(
                f"Producer: Request to {self._config[constants.PING_TARGET_WEBSITE_URL]} "
                f"timed out after {constants.PING_TIMEOUT_SECONDS} s."
            )
            response = None
        except requests.RequestException as e:
            logging.debug(f"Producer: RequestException. {e}.")
            response = None

        return response


    def collect_results(self, response: requests.Response) -> dict:
        """
        Analyze and refine a received HTTP response into a ping observation.
        """
        utc_now = datetime.datetime.utcnow()

        if response is None:
            return self.render_missed_observation(utc_now)

        results = PingObservation(
            utc_now,
            response.elapsed,
            response.status_code,
            self.check_for_regex_match(response)
        )

        return results


    def render_missed_observation(self, utc_now):
        """
        Returns a PingObservation that represents an unanswered
        HTTP request.
        """
        results = PingObservation(
            utc_now,
            None,
            None,
            None
        )
        return results


    def check_for_regex_match(self, response: requests.Response) -> bool:
        """
        Returns True if the text body of the response contained
        a match against the configured regex pattern.
        """
        regex_pattern = self._config[constants.PING_REGEX_PATTERN]
        target_text = response.text

        match = re.search(regex_pattern, target_text)
        return match is not None
