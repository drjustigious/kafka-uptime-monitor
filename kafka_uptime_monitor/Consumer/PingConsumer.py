import logging
import json
import datetime
import statistics
import psycopg2

from kafka import KafkaConsumer
from dataclasses import dataclass, fields
from dotenv import load_dotenv
from kafka_uptime_monitor import constants, utils
from kafka_uptime_monitor.Consumer import sql



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
                constants.USE_SSL,
            ], converter=int),

            # String parameters.
            **utils.load_from_env([
                constants.KAFKA_TOPIC,
                constants.KAFKA_GROUP,
                constants.KAFKA_BOOTSTRAP_URL,

                constants.LOG_FILENAME_BASE,

                constants.PSQL_HOST,
                constants.PSQL_USERNAME,
                constants.PSQL_PASSWORD,
                constants.PSQL_DATABASE_NAME,
                constants.PSQL_PORT,
                constants.PSQL_AGGREGATE_TABLE_NAME
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


    def run(self, quit_after_num_messages=None):
        """
        Keep checking for messages on the Kafka cluster
        until somebody tells the process to hang up (e.g. Ctrl+C).

        Passing an integer to 'quit_after_num_messages' will cause
        the consumer to shut down after processing the given number
        of messages. Useful for testing.
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
        num_messages_processed = 0
        for message in self._kafka_consumer:
            # This loop will continue as long as the Kafka connection is alive.
            self.collect_message(message.value)
            num_messages_processed += 1
            if quit_after_num_messages is not None and num_messages_processed >= quit_after_num_messages:
                break

        logging.warn(f"Consumer: Exiting.")


    def configure_kafka_consumer(self, config):
        if config[constants.USE_SSL]:
            logging.warn("Configuring Kafka consumer to use SSL. Looking for the following files: {}, {}, {}".format(
                constants.SSL_CAFILE,
                constants.SSL_CERTFILE,
                constants.SSL_KEYFILE
            ))            
            consumer = KafkaConsumer(
                config[constants.KAFKA_TOPIC],
                bootstrap_servers=[config[constants.KAFKA_BOOTSTRAP_URL]],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id=config[constants.KAFKA_GROUP],
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))    ,
                security_protocol="SSL",
                ssl_cafile=constants.SSL_CAFILE,
                ssl_certfile=constants.SSL_CERTFILE,
                ssl_keyfile=constants.SSL_KEYFILE,                     
            )
        else:
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
        logging.debug(f"Consumer: Collected message. {message}")
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
        self.ensure_db_schema_exists()
        self.write_aggregate_to_database(aggregate)


    def ensure_db_schema_exists(self):
        """
        Check that the necessary PSQL table(s) exist for persisting the
        aggregated uptime data.
        """
        with self.get_psql_connection() as conn:
            with conn.cursor() as cur:
                columns = []
                for field in fields(ObservationAggregate):
                    column_type_string = constants.PYTHON_TYPES_AS_PSQL_COLUMNS.get(field.type)
                    column_string = f"{field.name} {column_type_string}"
                    columns.append(column_string)

                cur.execute(sql.create_table(
                    self._config[constants.PSQL_AGGREGATE_TABLE_NAME],
                    columns
                ))

                conn.commit()


    def write_aggregate_to_database(self, aggregate):
        """
        Write a database row describing the given aggregate.
        """
        with self.get_psql_connection() as conn:
            with conn.cursor() as cur:
                column_value_pairs = []
                for field in fields(aggregate):
                    field_name = field.name
                    field_value = getattr(aggregate, field.name)
                    column_value_pairs.append((field_name, field_value))

                sql_template_string, values = sql.update(
                    self._config[constants.PSQL_AGGREGATE_TABLE_NAME],
                    column_value_pairs
                )
                cur.execute(sql_template_string, values)                    
                conn.commit()


    def get_psql_connection(self):
        """
        Initializes and returns a PSQL connection object.
        """
        conn = psycopg2.connect(
            dbname      = self._config[constants.PSQL_DATABASE_NAME],
            user        = self._config[constants.PSQL_USERNAME],
            password    = self._config[constants.PSQL_PASSWORD],
            host        = self._config[constants.PSQL_HOST],
            port        = self._config[constants.PSQL_PORT],
        )

        return conn