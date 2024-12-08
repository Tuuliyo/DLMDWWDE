#!/bin/bash

# Retry mechanism to load environment variables
MAX_ATTEMPTS=5
ATTEMPT=1
SLEEP_TIME=5  # Time to wait between attempts

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if [ -f "/vault-secrets/.env" ]; then
        echo "Loading environment variables from /vault-secrets/.env..."
        export $(grep -v '^#' /vault-secrets/.env | xargs)
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


# URLs of Solace broker's health check endpoints
SOLACE_BROKER_URL_GUARANTEED="$BROKER_HEALTH_PROTOCOL://$BROKER_HOST:$BROKER_HEALTH_PORT/health-check/guaranteed-active"
SOLACE_BROKER_URL_DIRECT="$BROKER_HEALTH_PROTOCOL://$BROKER_HOST:$BROKER_HEALTH_PORT/health-check/direct-active"
VALIDATION_SERVICE_URL="$API_PROTOCOL://$API_HOST:$API_PORT/validation-service/api/v1/health"
MAX_ATTEMPTS=10
ATTEMPT=1
SLEEP_TIME=5  # Time to wait between attempts

echo "Waiting for message broker and validation service to be healthy..."

while :; do
    # Check the first health endpoint
    curl --silent --fail $SOLACE_BROKER_URL_GUARANTEED
    GUARANTEED_STATUS=$?
    
    # Check the second health endpoint
    curl --silent --fail $SOLACE_BROKER_URL_DIRECT
    DIRECT_STATUS=$?

    # Check the validation service health endpoint
    curl --silent --fail $VALIDATION_SERVICE_URL
    VALIDATION_SERVICE_STATUS=$?

    # Both health checks must succeed (status 0 indicates success)
    if [ $GUARANTEED_STATUS -eq 0 ] && [ $DIRECT_STATUS -eq 0 ] && [ $VALIDATION_SERVICE_STATUS -eq 0 ]; then
        echo "All health checks passed successfully."
        break
    fi

    if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
        echo "All health checks failed after $MAX_ATTEMPTS attempts. Exiting..."
        exit 1
    fi

    echo "Attempt $ATTEMPT of $MAX_ATTEMPTS failed. Retrying in $SLEEP_TIME seconds..."
    ATTEMPT=$((ATTEMPT+1))
    sleep $SLEEP_TIME
done

echo "Starting Aggregation service..."
exec python -m bytewax.run src/main.py