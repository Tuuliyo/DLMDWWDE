#!/bin/sh

# ------------------------------------------------------------------------------
# Script to Populate Vault Secrets for Otel Collector Service
# This script generates configuration details, and populates
# them into Vault using the `vault kv put` command.
# ------------------------------------------------------------------------------

# Environment variables
SECRETS_BASE_PATH="kv/otel-collector"
OTEL_PROTOCOL="http"
OTEL_HOST="otel-collector"
OTEL_PORT="4317"
TEMPO_HOST="tempo"
TEMPO_PORT="4317"

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

# Populate Vault secrets
echo "Populating data at $SECRETS_BASE_PATH/config..."
vault kv put $SECRETS_BASE_PATH/config \
    otel_protocol="$OTEL_PROTOCOL" \
    otel_host="$OTEL_HOST" \
    otel_port="$OTEL_PORT" \
    tempo_host="$TEMPO_HOST" \
    tempo_port="$TEMPO_PORT"

echo "Data for otel collector service populated successfully."
