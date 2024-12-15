# ------------------------------------------------------------------------------
# Dockerfile for Python FastAPI Application
# Base Image: python:3.11-slim
# Purpose: Runs a FastAPI application with Uvicorn
# ------------------------------------------------------------------------------

# Use the official slim Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
# This is used to install application dependencies
COPY requirements.txt /app/

# Install Python dependencies without caching to keep the image lightweight
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the container
COPY src/ /app/src/

# Set the PYTHONPATH environment variable for module resolution
ENV PYTHONPATH=/app/src

# Expose the application port (default for FastAPI/Uvicorn is 8000)
EXPOSE 8000

# Define the default command to run the FastAPI application using Uvicorn
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "error"]
