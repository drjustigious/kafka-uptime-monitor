kafka-uptime-monitor
---

### Using Apache Kafka and PostgreSQL to monitor a web site's quality of service.

This is a lightweight tech demo and practice project comprising two main components:
- An Apache Kafka producer that periodically checks the status of a given web site using HTTP requests.
- An Apache Kafka consumer that aggregates the periodic checks into statistics stored in a PostgreSQL database.
