import argparse
import sys

from kafka_uptime_monitor.Producer.PingProducer import PingProducer
from kafka_uptime_monitor.Consumer.PingConsumer import PingConsumer


def main(launch_producer, launch_consumer):
    """
    Launch either a ping producer or ping consumer
    on the local machine.
    """ 

    if launch_consumer:
        PingConsumer().run()
    if launch_producer:
        PingProducer().run()

    
if __name__ == "__main__":
    """
    The entry point of the project code when used for demonstration purposes.
    Running this without command line arguments will print out argparse's
    default usage instructions.
    """
    parser = argparse.ArgumentParser(description="Launch either a kafka-uptime-monitor ping producer or ping consumer on the local machine.")
    parser.add_argument(
        "-p",
        action="store_true",
        help=(
            "Launch a ping producer. This component periodically checks the "
            "responsiveness of the target web site and publishes each ping in Kafka."
        )
    )
    parser.add_argument(
        "-c",
        action="store_true",
        help=(
            "Launch a ping consumer. This component collects ping observations "
            "from Kafka and consolidates them into a PostgreSQL database."
        )
    )

    args = parser.parse_args()

    launch_producer = args.p
    launch_consumer = args.c

    if launch_producer and launch_consumer:
        # The user tried to start both the producer and consumer.
        print("Please choose either -p or -c.")
        sys.exit()

    if not launch_producer and not launch_consumer:
        # The user did not ask for either the producer or the consumer.
        parser.print_help()
        sys.exit()             
    
    main(launch_producer, launch_consumer)