from dotenv import load_dotenv

from kafka_uptime_monitor.Producer.PingProducer import PingProducer

async def main():
    """
    Launch both a ping producer and ping consumer side by side
    on the local machine.
    """
    load_dotenv()
    PingProducer().run()
    
if __name__ == "__main__":
    main()