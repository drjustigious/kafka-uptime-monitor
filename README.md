kafka-uptime-monitor
---

### Using Apache Kafka and PostgreSQL to monitor a web site's quality of service.

This is a lightweight tech demo and practice project comprising two main components:
- An Apache Kafka producer that periodically checks the status of a given web site using HTTP requests.
- An Apache Kafka consumer that aggregates the periodic checks into statistics stored in a PostgreSQL database.

---
This project uses *Poetry* to manage dependencies.

> https://python-poetry.org/

To set the project up in a fresh virtual Python environment, `cd` to the directory where you find this README.md after cloning the project from GitHub and run the following (assuming you're on Ubuntu 20.04 or a compatible OS):

```
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install
```