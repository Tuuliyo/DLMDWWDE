# ------------------------------------------------------------------------------
# Dockerfile for creating a lightweight Python environment for a Bytewax application.
# - Uses Python 3.11 slim as the base image.
# - Installs required Python dependencies and minimal system utilities.
# - Ensures a clean and optimized image for production use.
# ------------------------------------------------------------------------------

# Use the official slim Python 3.11 image as the base image
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container's working directory
COPY requirements.txt /app/

# Install Python dependencies from requirements.txt
# The --no-cache-dir option ensures that no cache files are left behind, reducing image size.
RUN pip install --no-cache-dir -r requirements.txt

# Install curl and perform cleanup to minimize the image size
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the source code into the container's /app/src directory
COPY src/ /app/src/

# Set the default command to run the Bytewax application
CMD ["python", "-m", "bytewax.run", "src/main.py"]
