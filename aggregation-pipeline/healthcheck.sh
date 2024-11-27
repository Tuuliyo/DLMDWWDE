#!/bin/bash
# URLs of Solace broker's health check endpoints
SOLACE_BROKER_URL_GUARANTEED="http://message-broker:5550/health-check/guaranteed-active"
SOLACE_BROKER_URL_DIRECT="http://message-broker:5550/health-check/direct-active"
MAX_ATTEMPTS=10
ATTEMPT=1
SLEEP_TIME=5  # Time to wait between attempts

echo "Waiting for message broker to be healthy..."

while :; do
    # Check the first health endpoint
    curl --silent --fail $SOLACE_BROKER_URL_GUARANTEED
    GUARANTEED_STATUS=$?
    
    # Check the second health endpoint
    curl --silent --fail $SOLACE_BROKER_URL_DIRECT
    DIRECT_STATUS=$?

    # Both health checks must succeed (status 0 indicates success)
    if [ $GUARANTEED_STATUS -eq 0 ] && [ $DIRECT_STATUS -eq 0 ]; then
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
exec python -m bytewax.run -w3 src/refactored.py