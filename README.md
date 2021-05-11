kafka-uptime-monitor
---

### Using Apache Kafka and PostgreSQL to monitor a web site's quality of service.

This is a lightweight tech demo and practice project comprising two main components:
- An Apache Kafka producer that periodically checks the status of a given web site using HTTP requests.
- An Apache Kafka consumer that aggregates the periodic checks into statistics stored in a PostgreSQL database.

---
This project uses *Poetry* to manage dependencies.

> https://python-poetry.org/

To set the project up after a fresh git clone, `cd` to the directory where you find this README.md. There you will also find an executable configuration script called `configure.sh`. Running that script will accomplish the following setup steps:
- Create a virtual Python environment for the project if one does not exist yet.
- Install dependencies using Poetry.
- Set up an .env file to store your connection secrets (your default editor will open for editing the .env).
- Run the test suite.
- Print usage instructions.

It is safe to run `configure.sh` multiple times e.g. if you need to adjust the .env settings. The script should be essentially idempotent.