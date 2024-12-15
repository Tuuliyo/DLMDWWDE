#!/bin/sh

# ------------------------------------------------------------------------------
# Script to Populate Vault Secrets for Validation Service
# This script generates secure credentials, configures API details, and populates
# them into Vault using the `vault kv put` command.
# ------------------------------------------------------------------------------

# Constants
PASSWORD_LENGTH=16
SPECIAL_CHARS=true

# Function to generate a secure password
generate_password() {
    if [ "$SPECIAL_CHARS" = true ]; then
        tr -dc 'A-Za-z0-9!#$%*_+?' </dev/urandom | head -c $PASSWORD_LENGTH
    else
        tr -dc 'A-Za-z0-9' </dev/urandom | head -c $PASSWORD_LENGTH
    fi
}

# Environment variables
SECRETS_BASE_PATH="kv/validation-service"
API_PROTOCOL="http"
API_HOST="traefik"
API_PORT="80"
AGGREGATION_SERVICE_USERNAME="aggregation-service_username"
AGGREGATION_SERVICE_PASSWORD=$(generate_password)
POS_SERVICE_USERNAME="pos-service_username"
POS_SERVICE_PASSWORD=$(generate_password)

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

# Populate Vault secrets
echo "Populating data at $SECRETS_BASE_PATH/config..."
vault kv put $SECRETS_BASE_PATH/config \
    api_protocol="$API_PROTOCOL" \
    api_host="$API_HOST" \
    api_port="$API_PORT"

echo "Populating data at $SECRETS_BASE_PATH/creds/aggregation-service..."
vault kv put $SECRETS_BASE_PATH/creds/aggregation-service \
    username="$AGGREGATION_SERVICE_USERNAME" \
    password="$AGGREGATION_SERVICE_PASSWORD"

echo "Populating data at $SECRETS_BASE_PATH/creds/pos-service..."
vault kv put $SECRETS_BASE_PATH/creds/pos-service \
    username="$POS_SERVICE_USERNAME" \
    password="$POS_SERVICE_PASSWORD"

echo "Data for validation service populated successfully."
