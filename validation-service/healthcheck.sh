#!/bin/bash

# ------------------------------------------------------------------------------
# Shell Script to Load Environment Variables and Start Validation Service
# This script:
# - Retries loading environment variables from a `.env` file stored in `/vault-secrets`.
# - Checks for valid entries in the `.env` file.
# - Starts the FastAPI application using Uvicorn if the environment is configured correctly.
# ------------------------------------------------------------------------------

# Constants for retry mechanism
MAX_ATTEMPTS=5    # Maximum number of retry attempts
SLEEP_TIME=5      # Time in seconds to wait between attempts
ATTEMPT=1         # Counter for the current retry attempt

# Retry mechanism to load environment variables
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if [ -f "/vault-secrets/.env" ]; then
        echo "Found /vault-secrets/.env. Checking for valid entries..."
        
        # Check if the file contains at least one non-commented line
        if grep -q -E '^[^#[:space:]]' /vault-secrets/.env; then
            echo "Loading environment variables from /vault-secrets/.env..."
            # Export all non-commented environment variables
            export $(grep -v '^#' /vault-secrets/.env | xargs)
            echo "Environment variables loaded successfully."
            break
        else
            echo "Attempt $ATTEMPT: /vault-secrets/.env is empty or contains only comments."
        fi
    else
        echo "Attempt $ATTEMPT: Environment file /vault-secrets/.env not found."
    fi

    # Check if maximum attempts have been reached
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "Failed to load environment variables after $MAX_ATTEMPTS attempts. Exiting..."
        exit 1
    fi

    # Increment the attempt counter and wait before retrying
    ATTEMPT=$((ATTEMPT + 1))
    sleep $SLEEP_TIME
done

# Start the Validation service using Uvicorn
echo "Starting Validation service..."
exec uvicorn src.app:app --host 0.0.0.0 --port 8000 --log-level error
