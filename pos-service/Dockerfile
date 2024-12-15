# ------------------------------------------------------------------------------
# Dockerfile for creating a Python-based container for running a Python application.
# This image includes:
# - Python 3.11 slim as the base image.
# - Installation of Python dependencies.
# - Additional utilities like curl.
# - A clean, lightweight setup for production.
# ------------------------------------------------------------------------------

# Use the official slim Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements.txt file from the host to the container
COPY requirements.txt /app/

# Install the Python dependencies specified in requirements.txt
# The --no-cache-dir option ensures a smaller image size by avoiding unnecessary files.
RUN pip install --no-cache-dir -r requirements.txt

# Update the package list and install curl
# Use --no-install-recommends to avoid installing unnecessary packages
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the application source code into the container
COPY src/ /app/src/

# Define the default command to run the Python application
CMD ["python", "src/app.py"]
