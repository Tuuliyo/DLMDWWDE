# Use the official slim Python 3.11 image as the base image
# This provides a lightweight Python environment suitable for production.
FROM python:3.11-slim

# Set the working directory inside the container to /app
# All subsequent commands and paths will be relative to this directory.
WORKDIR /app

# Copy the requirements.txt file from the host to the container's /app directory
# This file contains a list of dependencies required by the Python application.
COPY requirements.txt /app/

# Install the Python dependencies specified in requirements.txt
# The --no-cache-dir option ensures that the installation does not leave behind unnecessary files.
RUN pip install --no-cache-dir -r requirements.txt

# Update the package list and install curl for additional utility
# The --no-install-recommends flag avoids unnecessary recommended packages.
# After installation, clean up the package cache to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the contents of the src directory from the host to the container's /app/src directory
# This step ensures that the application code is included in the container.
COPY src/ /app/src/

# Set the default command to run the Bytewax application
# This executes the main.py script located in the src directory using Python.
CMD ["python", "-m", "bytewax.run", "src/main.py"]
