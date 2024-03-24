# MyApp - A Flask Application with User Authentication and Tracing

This application demonstrates the use of Flask to create a web application with user authentication, database operations, administrative interface, form handling, and observability through tracing with OpenTelemetry and Jaeger.

## Features

- User authentication (login and logout)
- User registration with dynamic nationality selection
- Password hashing
- Admin interface for managing users
- Observability with OpenTelemetry and Jaeger

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6+
- pip (Python package installer)
- Docker (for running Jaeger)

## Installation

Follow these steps to get your development environment set up:

1. **Clone the repository**

```bash
git clone https://yourrepository.com/yourproject.git
cd yourproject
```

2. **Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. **Install the required Python packages**

```bash
pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Flask-Admin Werkzeug pycountry opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask opentelemetry-exporter-jaeger
```

4. **Run Jaeger using Docker**

To capture and visualize the traces from our application, we'll run Jaeger in a Docker container:

```bash
docker run -d --name jaeger \
  -e COLLECTOR_ZIPKIN_HTTP_PORT=9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 9411:9411 \
  jaegertracing/all-in-one:latest
```

This command starts Jaeger locally and exposes its UI on [http://localhost:16686](http://localhost:16686).

5. **Initialize the Database**

Before running the application for the first time, create the initial database:

```bash
python
>>> from app import db
>>> db.create_all()
>>> exit()
```

## Running the Application

To start the application, use the following command:

```bash
flask run
```

The application will be available at [http://localhost:5000](http://localhost:5000).

## Using the Application

- Navigate to [http://localhost:5000/register](http://localhost:5000/register) to create a new user.
- After registration, log in at [http://localhost:5000/login](http://localhost:5000/login).
- Access the dashboard at [http://localhost:5000/dashboard](http://localhost:5000/dashboard) (login required).
- Admin interface can be accessed at [http://localhost:5000/admin](http://localhost:5000/admin) with appropriate credentials.
- To observe tracing data, visit the Jaeger UI at [http://localhost:16686](http://localhost:16686).

## Contributing

Contributions to this project are welcome! Please fork the repository and submit a pull request with your improvements.

## License

Specify your project's license here.

---

Adapt and fill in the sections as needed to better match your project's specifics and requirements.

