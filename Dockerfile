# Use an official Python runtime as a parent image
FROM python:3.11

# Create and set the working directory
RUN mkdir /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y gettext


# Copy the rest of application code into the container at /app
COPY . /app/

# Run database migrations and collectstatic data
RUN python manage.py migrate
RUN python manage.py collectstatic
RUN django-admin compilemessages


# Expose the port
EXPOSE 8000

# Check if .env file exists, and if it does, use it to set environment variables
RUN if [ -f .env ]; then echo "Using .env file"; else echo "Using environment variables"; fi
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "weather_api.asgi:application"]
