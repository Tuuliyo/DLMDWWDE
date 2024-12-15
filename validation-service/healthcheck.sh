#!/bin/bash

# Retry mechanism to load environment variables
MAX_ATTEMPTS=5
ATTEMPT=1
SLEEP_TIME=5  # Time to wait between attempts

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if [ -f "/vault-secrets/.env" ]; then
        echo "Found /vault-secrets/.env. Checking for valid entries..."
        
        # Check if the file contains at least one non-commented line
        if grep -q -E '^[^#[:space:]]' /vault-secrets/.env; then
            echo "Loading environment variables from /vault-secrets/.env..."
            export $(grep -v '^#' /vault-secrets/.env | xargs)
            echo "Environment variables loaded successfully."
            break
        else
            echo "Attempt $ATTEMPT: /vault-secrets/.env is empty or contains only comments."
        fi
    else
        echo "Attempt $ATTEMPT: Environment file /vault-secrets/.env not found."
    fi

    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "Failed to load environment variables after $MAX_ATTEMPTS attempts. Exiting..."
        exit 1
    fi

    ATTEMPT=$((ATTEMPT + 1))
    sleep $SLEEP_TIME
done

# Start the POS service once the broker and validation service is healthy
echo "Starting Validation service..."
#exec python /app/src/app.py
exec uvicorn src.app:app --host 0.0.0.0 --port 8000 --log-level error