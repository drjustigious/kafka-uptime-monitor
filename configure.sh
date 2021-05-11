#! /bin/bash

echo "Configuring kafka-uptime-monitor."
echo "Setting up virtual Python environment."
python3 -m venv venv
source venv/bin/activate

echo "Installing poetry for dependency management."
pip install poetry
echo "Installing dependencies through poetry."
poetry install

echo "Please edit .env to match your database environment and preferences."
cp kafka_uptime_monitor/sample.env kafka_uptime_monitor/.env
vim .env

echo "Running test suite."
python tests/test_kafka_uptime_monitor.py