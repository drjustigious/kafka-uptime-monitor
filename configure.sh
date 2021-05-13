#! /bin/bash

echo "Configuring kafka-uptime-monitor."
echo "Setting up virtual Python environment."
python3 -m venv venv
source venv/bin/activate

echo "Installing poetry for dependency management."
pip install poetry
echo "Installing dependencies through poetry."
poetry install

echo -e "\nPlease edit .env to match your database environment and preferences. An editor will open shortly."
sleep 5
if [ ! -f kafka_uptime_monitor/.env ]; then
    cp kafka_uptime_monitor/sample.env kafka_uptime_monitor/.env
fi
"${EDITOR:-${VISUAL:-vi}}" kafka_uptime_monitor/.env

echo -e "\nRunning test suite. This can take about a minute."
sleep 3
python tests/test_kafka_uptime_monitor.py

echo -e "\nTests completed.\n\nPlease type the following to run the producer and consumer individually:"
echo "  source venv/bin/activate                  # Activate the virtual environment."
echo "  python kafka_uptime_monitor/main.py -p &  # Run Kafka producer."
echo "  python kafka_uptime_monitor/main.py -c &  # Run Kafka consumer."