import datetime

# Recognized environment variables.
PING_TARGET_WEBSITE_URL = "PING_TARGET_WEBSITE_URL"
PING_INTERVAL_SECONDS = "PING_INTERVAL_SECONDS"
PING_TIMEOUT_SECONDS = "PING_TIMEOUT_SECONDS"
PING_REGEX_PATTERN = "PING_REGEX_PATTERN"

AGGREGATION_SAMPLE_COUNT = "AGGREGATION_SAMPLE_COUNT"

LOG_FILENAME_BASE = "LOG_FILENAME_BASE"
LOG_LEVEL = "LOG_LEVEL"
KAFKA_TOPIC = "KAFKA_TOPIC"
KAFKA_BOOTSTRAP_URL = "KAFKA_BOOTSTRAP_URL"
KAFKA_GROUP = "KAFKA_GROUP"

PSQL_HOST = "PSQL_HOST"
PSQL_DATABASE_NAME = "PSQL_DATABASE_NAME"
PSQL_USERNAME = "PSQL_USERNAME"
PSQL_PASSWORD = "PSQL_PASSWORD"
PSQL_PORT = "PSQL_PORT"
PSQL_AGGREGATE_TABLE_NAME = "PSQL_AGGREGATE_TABLE_NAME"

USE_SSL = "USE_SSL"


# Python-side constants.
LOGGING_FORMAT = '[%(asctime)s] %(levelname)s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
CONSUMER_LOGFILE_SUFFIX = "_consumer.log"
PRODUCER_LOGFILE_SUFFIX = "_producer.log"
RESPONSE_OK = 200
PYTHON_TYPES_AS_PSQL_COLUMNS = {
    datetime.datetime: "timestamp",
    int: "integer",
    float: "real",
}

SSL_CAFILE = "certs/ca.pem"
SSL_CERTFILE = "certs/service.cert"
SSL_KEYFILE = "certs/service.key"


# Python-side keys.
LOG_FILE_NAME = "LOG_FILE_NAME"
OBSERVATION_TIME = "observation_time"
RESPONSE_TIME = "response_time"
RESPONSE_STATUS = "response_status"
REGEX_MATCHED = "regex_matched"