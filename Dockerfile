# Base image with Python 3.8 and Debian
FROM python:3.8-slim-buster

# Install RabbitMQ and enable the management plugin
RUN apt-get update && apt-get install -y --no-install-recommends rabbitmq-server \
    && rabbitmq-plugins enable rabbitmq_management \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory for the container
WORKDIR /app

# Copy the requirements.txt file to the container and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Set environment variables for Celery
ENV CELERY_BROKER_URL amqp://guest:guest@localhost:5672//

# Set environment variables for Flask
ENV FLASK_APP app.py
ENV FLASK_ENV production

# Expose the port that the Flask app will run on
EXPOSE 5000

# Set the entry point for the container to start RabbitMQ and run the Flask app with gunicorn and start celery worker
ENTRYPOINT ["service", "rabbitmq-server", "start", "&&", "gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "1", "--timeout", "3600", "--keep-alive", "180", "--preload", "&&", "celery", "-A", "app.celery", "worker", "--loglevel=INFO", "--concurrency=1", "--time-limit=3600", "-Ofair"]

