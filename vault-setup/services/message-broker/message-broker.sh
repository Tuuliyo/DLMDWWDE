#!/bin/sh

# Password length and options
PASSWORD_LENGTH=16
SPECIAL_CHARS=true

# Function to generate a secure password
generate_password() {
    if [ "$SPECIAL_CHARS" = true ]; then
        tr -dc 'A-Za-z0-9!@#$%*_+?' </dev/urandom | head -c $PASSWORD_LENGTH
    else
        # Generate a password without special characters
        tr -dc 'A-Za-z0-9' </dev/urandom | head -c $PASSWORD_LENGTH
    fi
}

# Variables
SECRETS_BASE_PATH="kv/message-broker"
HTTP_HOST="message-broker"
HTTP_PORT="8080"
HTTP_PROTOCOL="http"
SMF_HOST="message-broker"
SMF_PORT="55555"
SMF_PROTOCOL="tcp"
HEALTH_HOST="message-broker"
HEALTH_PORT="5550"
HEALTH_PROTOCOL="http"
AMQP_HOST="message-broker"
AMQP_PORT="5672"
MSG_VPN="default"
POS_TOPIC_PREFIX="sale/pos/transaction"
LOGIN_USERNAME="admin"
LOGIN_PASSWORD="admin"
OTEL_USERNAME="telemetry_collector_service"
OTEL_PASSWORD=$(generate_password)
VALIDATION_SERVICE_USERNAME="sale_pos_transaction_validation"
VALIDATION_SERVICE_PASSWORD=$(generate_password)
AGGREGATION_SERVICE_USERNAME="sale_pos_transaction_aggregation"
AGGREGATION_SERVICE_PASSWORD=$(generate_password)
AGGREGATION_SERVICE_QUEUE_NAME="sale_pos_transaction_aggregation_service"

# Verify VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
    echo "Error: VAULT_ADDR is not set. Please export VAULT_ADDR before running this script."
    exit 1
fi

echo "Populating data at $SECRETS_BASE_PATH/config..."
vault kv put $SECRETS_BASE_PATH/config \
    http_host="$HTTP_HOST" \
    http_port="$HTTP_PORT" \
    http_protocol="$HTTP_PROTOCOL" \
    smf_host="$SMF_HOST" \
    smf_port="$SMF_PORT" \
    smf_protocol="$SMF_PROTOCOL" \
    health_host="$HEALTH_HOST" \
    health_port="$HEALTH_PORT" \
    health_protocol="$HEALTH_PROTOCOL" \
    amqp_host="$AMQP_HOST" \
    amqp_port="$AMQP_PORT" \
    msg_vpn="$MSG_VPN" \
    pos_topic_prefix="$POS_TOPIC_PREFIX" \

echo "Populating data at $SECRETS_BASE_PATH/config/aggregation-service..."
vault kv put $SECRETS_BASE_PATH/config/aggregation-service \
    queue_name="$AGGREGATION_SERVICE_QUEUE_NAME"

echo "Populating data at $SECRETS_BASE_PATH/creds/login..."
vault kv put $SECRETS_BASE_PATH/creds/login \
    username="$LOGIN_USERNAME" \
    password="$LOGIN_PASSWORD"

echo "Populating data at $SECRETS_BASE_PATH/creds/otel..."
vault kv put $SECRETS_BASE_PATH/creds/otel \
    username="$OTEL_USERNAME" \
    password="$OTEL_PASSWORD"

echo "Populating data at $SECRETS_BASE_PATH/creds/validation-service..."
vault kv put $SECRETS_BASE_PATH/creds/validation-service \
    username="$VALIDATION_SERVICE_USERNAME" \
    password="$VALIDATION_SERVICE_PASSWORD"

echo "Populating data at $SECRETS_BASE_PATH/creds/aggregation-service..."
vault kv put $SECRETS_BASE_PATH/creds/aggregation-service \
    username="$AGGREGATION_SERVICE_USERNAME" \
    password="$AGGREGATION_SERVICE_PASSWORD"

echo "Data for validation service populated successfully."
