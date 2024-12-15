#!/bin/sh

# Variables
SECRETS_BASE_PATH="kv/solace-prometheus-exporter"
LISTEN_ADDR_HOST="0.0.0.0"
LISTEN_ADDR_PORT="9628"
TIMEOUT="5s"
SSL_VERIFY="false"
LISTEN_TLS="false"

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

echo "Populating data at $SECRETS_BASE_PATH/config..."
vault kv put $SECRETS_BASE_PATH/config \
    listen_addr_host="$LISTEN_ADDR_HOST" \
    listen_addr_port="$LISTEN_ADDR_PORT" \
    timeout="$TIMEOUT" \
    ssl_verify="$SSL_VERIFY" \
    listen_tls="$LISTEN_TLS"

echo "Data for validation service populated successfully."
