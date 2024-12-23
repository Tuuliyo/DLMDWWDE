#!/bin/bash

# ------------------------------------------------------------------------------
# Script to load environment variables, perform health checks, and start the POS service.
# This script ensures:
# 1. Environment variables are loaded from HashiCorp Vault's secrets.
# 2. Solace broker and validation service health are verified before starting.
# 3. The POS service is started only after all health checks pass.
# ------------------------------------------------------------------------------

# Retry mechanism for loading environment variables
MAX_ATTEMPTS=5          # Maximum number of attempts to load environment variables
ATTEMPT=1               # Current attempt counter
SLEEP_TIME=5            # Wait time (in seconds) between attempts

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if [ -f "/vault-secrets/.env" ]; then
        echo "Found /vault-secrets/.env. Checking for valid entries..."
        
        # Verify that the file contains at least one non-commented line
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

# URLs for Solace broker's health check endpoints
SOLACE_BROKER_URL_GUARANTEED="$BROKER_PROTOCOL://$BROKER_HOST:$BROKER_PORT/health-check/guaranteed-active"
SOLACE_BROKER_URL_DIRECT="$BROKER_PROTOCOL://$BROKER_HOST:$BROKER_PORT/health-check/direct-active"
VALIDATION_SERVICE_URL="$API_PROTOCOL://$API_HOST:$API_PORT/validation-service/api/v1/health"

# Retry mechanism for health checks
MAX_ATTEMPTS=10          # Maximum number of attempts to verify health
ATTEMPT=1                # Current attempt counter
SLEEP_TIME=5             # Wait time (in seconds) between health check attempts

echo "Waiting for message broker and validation service to be healthy..."

while :; do
    # Perform health checks for the broker and validation service
    curl --silent --fail $SOLACE_BROKER_URL_GUARANTEED
    GUARANTEED_STATUS=$?

    curl --silent --fail $SOLACE_BROKER_URL_DIRECT
    DIRECT_STATUS=$?

    curl --silent --fail $VALIDATION_SERVICE_URL
    VALIDATION_SERVICE_STATUS=$?

    # Check if all endpoints are healthy
    if [ $GUARANTEED_STATUS -eq 0 ] && [ $DIRECT_STATUS -eq 0 ] && [ $VALIDATION_SERVICE_STATUS -eq 0 ]; then
        echo "All health checks passed successfully."
        break
    fi

    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "All health checks failed after $MAX_ATTEMPTS attempts. Exiting..."
        exit 1
    fi

    echo "Attempt $ATTEMPT of $MAX_ATTEMPTS failed. Retrying in $SLEEP_TIME seconds..."
    ATTEMPT=$((ATTEMPT + 1))
    sleep $SLEEP_TIME
done

# Start the POS service after all checks pass
echo "Starting POS service..."
exec python /app/src/app.py
