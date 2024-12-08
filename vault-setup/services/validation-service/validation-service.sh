#!/bin/sh

# Variables
SECRETS_PATH="kv/validation-service"
BROKER_HOST="message-broker"
BROKER_PORT="55555"
BROKER_PROTOCOL="tcp"
BROKER_MSG_VPN="default"

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

echo "Populating data at $SECRETS_PATH..."
vault kv put $SECRETS_PATH \
    broker_host="$BROKER_HOST" \
    broker_port="$BROKER_PORT" \
    broker_protocol="$BROKER_PROTOCOL" \
    broker_msg_vpn="$BROKER_MSG_VPN"

echo "Data for validation service populated successfully."
