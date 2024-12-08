#!/bin/sh

# Variables
SECRETS_PATH="kv/pos-service"
API_HOST="traefik"
API_PORT="80"
API_PROTOCOL="http"
BROKER_HOST="message-broker"
BROKER_PORT="5550"
BROKER_PROTOCOL="http"

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

echo "Populating data at $SECRETS_PATH..."
vault kv put $SECRETS_PATH \
    api_host="$API_HOST" \
    api_port="$API_PORT" \
    api_protocol="$API_PROTOCOL" \
    broker_host="$BROKER_HOST" \
    broker_port="$BROKER_PORT" \
    broker_protocol="$BROKER_PROTOCOL"

echo "Data for pos service populated successfully."
