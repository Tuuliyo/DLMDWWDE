#!/bin/bash
# URLs of Solace broker's health check endpoints
SOLACE_BROKER_URL_GUARANTEED="http://message-broker:5550/health-check/guaranteed-active"
SOLACE_BROKER_URL_DIRECT="http://message-broker:5550/health-check/direct-active"
VALIDATION_SERVICE_URL="http://traefik/validation-service/api/v1/health"
MAX_ATTEMPTS=10
ATTEMPT=1
SLEEP_TIME=5  # Time to wait between attempts

echo "Waiting for message broker abd validation service to be healthy..."

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

# Start the POS service once the broker is healthy
echo "Starting POS service..."
exec python /app/src/app.py  # Replace with your actual command to start the POS service