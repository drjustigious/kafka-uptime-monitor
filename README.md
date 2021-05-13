kafka-uptime-monitor
---

### Using Apache Kafka and PostgreSQL to monitor a website's quality of service.

This is a lightweight tech demo and practice project comprising two main components:
- An Apache Kafka producer that periodically checks the status of a given web site using HTTP requests.
- An Apache Kafka consumer that aggregates the periodic checks into statistics stored in a PostgreSQL database.

While the tasks these components perform have some practical idea behind them, the producer and consumer are mostly just conceptual placeholders for an actual data sourcing and data refinement step, respectively. In particular, the data model of the statistics that the consumer writes to PostgreSQL was conceived during a period of time it took to consume a single cup of coffee.

The producer and consumer are both GUI-less command line applications written in Python 3.8.

### Main features
- Code written in Python 3.8 using only publicly available dependency packages.
- Extraction of runtime settings (including database secrets) from environment variables or a `.env` file.
- Routine to check if a particular website is up and healthy using HTTP requests.
  - Records the response status and response time.
  - Checks the content of the response by running a regular expression search. Records whether or not a regex match was found.
- Routine to push raw website health observations into an Apache Kafka cluster.
- Routine to draw raw website health observations from an Apache Kafka cluster.
- Routine to analyze and aggregate raw observations.
  - Includes counts of total observations, "no response", "response OK" and "content regex match OK".
  - Includes basic distribution stats over the response time (mean, median, min, max, standard deviation).
  - Includes observed uptime as a percentage.
- Routine to set up and update a PostgreSQL database table for storing the aggregated observations.
- Minimal suite of automatic tests; mainly just a smoke test for the whole solution.
- Shell script for automatically setting up a runtime environment for the solution.

---
### Setup notes

The project uses *Poetry* to manage dependencies.

> https://python-poetry.org/

To set the project up after a fresh git clone, `cd` to the directory where you find this README.md. There you will also find an executable configuration script called `configure.sh`. Running that script will accomplish the following:
- Creates a virtual Python environment for the project if one does not exist yet.
- Installs dependencies using Poetry.
- Sets up an .env file to store your connection secrets (your default editor will open for editing the .env).
- Runs the test suite.
- Prints usage instructions.

It is safe to run `configure.sh` multiple times e.g. if you need to adjust the .env settings. The script should be essentially idempotent.
