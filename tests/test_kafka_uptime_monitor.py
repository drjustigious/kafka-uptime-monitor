import logging
from kafka_uptime_monitor import __version__, utils, constants
from kafka_uptime_monitor.Producer.PingProducer import PingProducer
from kafka_uptime_monitor.Consumer.PingConsumer import PingConsumer


def test_version():
    print("Testing package version match.")
    assert __version__ == '0.1.0'


def test_required_environment_variables_set():
    print("Testing required environment variables are set.")

    config = {
        # Integer parameters.
        **utils.load_from_env([
            # Used by Kafka producer.
            constants.PING_INTERVAL_SECONDS,
            constants.PING_TIMEOUT_SECONDS,
            constants.LOG_LEVEL,
            constants.USE_SSL,

            # Used by Kafka consumer.
            constants.AGGREGATION_SAMPLE_COUNT,
            constants.LOG_LEVEL,
            constants.USE_SSL,
        ], converter=int),

        # String parameters.
        **utils.load_from_env([
            # Used by Kafka producer.
            constants.PING_TARGET_WEBSITE_URL,
            constants.PING_REGEX_PATTERN,
            constants.LOG_FILENAME_BASE,
            constants.KAFKA_TOPIC,
            constants.KAFKA_BOOTSTRAP_URL,

            # Used by Kafka consumer.
            constants.KAFKA_TOPIC,
            constants.KAFKA_GROUP,
            constants.KAFKA_BOOTSTRAP_URL,

            constants.LOG_FILENAME_BASE,

            constants.PSQL_HOST,
            constants.PSQL_USERNAME,
            constants.PSQL_PASSWORD,
            constants.PSQL_DATABASE_NAME,
            constants.PSQL_PORT        
        ], converter=None)
    }

    return config


def test_logger_can_write(config: dict):
    print("Testing the logger can write.")
    utils.configure_logger(config)
    logging.warn("Logger test successful.")


def test_producer_can_run(num_messages: int):
    print(f"Test-running Kafka producer for {num_messages} messages.")
    PingConsumer().run(quit_after_num_messages=num_messages)


def test_consumer_can_run(num_messages: int):
    print(f"Test-running Kafka consumer for {num_messages} messages.")    
    PingProducer().run(quit_after_num_messages=num_messages)


def run_tests():
    """
    Run the full suite of tests.
    """
    print("Running kafka-uptime-monitor test suite.")

    test_version()
    config = test_required_environment_variables_set()
    test_logger_can_write(config)
    test_producer_can_run(num_messages=config[constants.AGGREGATION_SAMPLE_COUNT])
    test_consumer_can_run(num_messages=config[constants.AGGREGATION_SAMPLE_COUNT])
    

run_tests()