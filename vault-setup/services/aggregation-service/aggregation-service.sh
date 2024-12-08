#!/bin/sh

# Variables
SECRETS_PATH="kv/aggregation-service"
BROKER_HOST="message-broker"
BROKER_HEALTH_PORT="5550"
BROKER_HEALTH_PROTOCOL="http"
BROKER_MSG_PORT="55555"
BROKER_MSG_PROTOCOL="tcp"
BROKER_MSG_VPN="default"
API_HOST="traefik"
API_PORT="80"
API_PROTOCOL="http"

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

echo "Populating data at $SECRETS_PATH..."
vault kv put $SECRETS_PATH \
    broker_host="$BROKER_HOST" \
    broker_port="$BROKER_MSG_PORT" \
    broker_protocol="$BROKER_MSG_PROTOCOL" \
    broker_msg_vpn="$BROKER_MSG_VPN" \
    broker_health_port="$BROKER_HEALTH_PORT" \
    broker_health_protocol="$BROKER_HEALTH_PROTOCOL" \
    api_host="$API_HOST" \
    api_port="$API_PORT" \
    api_protocol="$API_PROTOCOL" \

echo "Data for validation service populated successfully."
