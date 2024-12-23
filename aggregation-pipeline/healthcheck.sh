#!/bin/bash

# ------------------------------------------------------------------------------
# Script to load environment variables, verify health checks, and start the service.
# This script ensures robust startup by:
# 1. Loading environment variables from HashiCorp Vault.
# 2. Verifying the health of Solace broker and the validation service.
# 3. Starting the Bytewax aggregation service if all checks pass.
# ------------------------------------------------------------------------------

# Retry mechanism for loading environment variables
MAX_ATTEMPTS=5          # Maximum attempts to load environment variables
ATTEMPT=1               # Initial attempt counter
SLEEP_TIME=5            # Wait time (in seconds) between attempts

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if [ -f "/vault-secrets/.env" ]; then
        echo "Loading environment variables from /vault-secrets/.env..."
        export $(grep -v '^#' /vault-secrets/.env | xargs)  # Load non-commented lines as environment variables
        echo "Environment variables loaded successfully."
        break
    else
        echo "Attempt $ATTEMPT: Environment file /vault-secrets/.env not found."
        if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
            echo "Failed to load environment file after $MAX_ATTEMPTS attempts. Exiting..."
            exit 1
        fi
    fi
    ATTEMPT=$((ATTEMPT + 1))
    sleep $SLEEP_TIME
done

# URLs for Solace broker and validation service health checks
SOLACE_BROKER_URL_GUARANTEED="$BROKER_HEALTH_PROTOCOL://$BROKER_HEALTH_HOST:$BROKER_HEALTH_PORT/health-check/guaranteed-active"
SOLACE_BROKER_URL_DIRECT="$BROKER_HEALTH_PROTOCOL://$BROKER_HEALTH_HOST:$BROKER_HEALTH_PORT/health-check/direct-active"
VALIDATION_SERVICE_URL="$API_PROTOCOL://$API_HOST:$API_PORT/validation-service/api/v1/health"

MAX_ATTEMPTS=10          # Maximum attempts for health checks
ATTEMPT=1                # Initial attempt counter
SLEEP_TIME=5             # Wait time (in seconds) between health check attempts

echo "Waiting for message broker and validation service to be healthy..."

while :; do
    # Perform health checks
    curl --silent --fail $SOLACE_BROKER_URL_GUARANTEED
    GUARANTEED_STATUS=$?  # Capture exit code for guaranteed-active health check
    
    curl --silent --fail $SOLACE_BROKER_URL_DIRECT
    DIRECT_STATUS=$?      # Capture exit code for direct-active health check
    
    curl --silent --fail $VALIDATION_SERVICE_URL
    VALIDATION_SERVICE_STATUS=$?  # Capture exit code for validation service health check

    # All health checks must succeed (exit code 0 indicates success)
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

# Start the aggregation service if all health checks pass
echo "Starting Aggregation service..."
exec python -m bytewax.run src/main.py
