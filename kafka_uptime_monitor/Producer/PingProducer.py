import os
from kafka_uptime_monitor import constants

class PingProducer(object):
    def __init__(self):
        print("Ping target:", os.getenv(constants.PING_TARGET_WEBSITE_URL))