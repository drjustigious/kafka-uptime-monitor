import logging
import json
import datetime
import statistics

from kafka import KafkaConsumer
from dataclasses import dataclass
from dotenv import load_dotenv
from kafka_uptime_monitor import constants, utils



@dataclass
class ObservationAggregate:
    """
    A data model of aggregated ping obsevations.
    """
    first_observation: datetime.datetime
    last_observation: datetime.datetime
    num_observations: int
    num_no_response: int
    num_status_ok: int
    num_regex_ok: int
    response_time_average: int
    response_time_median: int
    response_time_stdev: int
    response_time_min: int
    response_time_max: int
    uptime_percentage: float



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

        # Received messages will be aggregated into slightly larger objects for storing
        # in a relational database (PostgreSQL). Keep them in a queue until aggregated.
        self._first_observation_time = None
        self._message_queue = []



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
            # This loop will continue as long as the Kafka connection is alive.
            self.collect_message(message.value)

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


    def collect_message(self, message):
        """
        Add the received message into the analysis/aggregation queue.
        Also check whether we should already dump the queue into PSQL.
        """
        logging.info(f"Consumer: Collected message. {message}")
        self._message_queue.append(message)
        aggregate = self.analyze_message_queue()
        self.persist_aggregate(aggregate)


    def analyze_message_queue(self):
        """
        Check if the message queue has enough content to construct an
        aggregated data point. If so, construct it and write to PSQL.
        """
        if not self._first_observation_time:
            # Record the starting point of a new group of observations.
            self._first_observation_time = datetime.datetime.utcnow()

        if len(self._message_queue) < self._config[constants.AGGREGATION_SAMPLE_COUNT]:
            # Not enough data for aggregation, let's keep growing the queue.
            return None

        # Looks like the queue was long enough to merit aggregation.
        aggregate = self.aggregate_queue(self._message_queue)
        
        # The next message will begin a new group of observations when it arrives.
        self._first_observation_time = None
        self._message_queue = []
        return aggregate


    def aggregate_queue(self, queue):

        num_observations = 0
        num_no_response = 0
        num_status_ok = 0
        num_regex_ok = 0
        response_times = []

        for message in queue:
            num_observations += 1

            response_time = message[constants.RESPONSE_TIME]
            if response_time is not None:
                response_times.append(response_time)
            else:
                num_no_response += 1

            if message[constants.RESPONSE_STATUS] == constants.RESPONSE_OK:
                num_status_ok += 1

            if message[constants.REGEX_MATCHED]:
                num_regex_ok += 1


        aggregate = ObservationAggregate(
            first_observation = self._first_observation_time,
            last_observation = datetime.datetime.utcnow(),
            num_observations = num_observations,
            num_no_response = num_no_response,
            num_status_ok = num_status_ok,
            num_regex_ok = num_regex_ok,
            response_time_average = statistics.mean(response_times) if response_times else None,
            response_time_median = statistics.median(response_times) if response_times else None,
            response_time_stdev = statistics.stdev(response_times) if response_times else None,
            response_time_min = min(response_times) if response_times else None,
            response_time_max  = max(response_times) if response_times else None,
            uptime_percentage = 100.0*num_status_ok/num_observations if num_observations > 0 else 0.00
        )

        return aggregate


    def persist_aggregate(self, aggregate: ObservationAggregate):
        """
        Store the given ObservationAggregate into PSQL.
        """
        if aggregate is None:
            return

        logging.info(f"Consumer: Persisting aggregation results. {aggregate}")