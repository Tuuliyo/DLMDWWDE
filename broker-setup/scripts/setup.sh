#!/bin/sh

# ------------------------------------------------------------------------------
# Script to load environment variables, check Solace broker readiness, and manage
# Terraform infrastructure deployment using HashiCorp Vault for configuration.
# ------------------------------------------------------------------------------

# Retry mechanism to load environment variables from Vault
MAX_ATTEMPTS=5              # Maximum number of attempts to load environment variables
ATTEMPT=1                   # Current attempt counter
SLEEP_TIME=5                # Wait time (in seconds) between attempts

sleep 10 # Wait for Vault to be ready - buffer for startup time

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if [ -f "/vault-secrets/.env" ]; then
        echo "Found /vault-secrets/.env. Checking for valid entries..."
        
        # Check if the file contains at least one non-commented line
        if grep -q -E '^[^#[:space:]]' /vault-secrets/.env; then
            echo "Loading environment variables from /vault-secrets/.env..."
            export $(grep -v '^#' /vault-secrets/.env | xargs) # Load non-commented lines as environment variables
            echo "Environment variables loaded successfully." 
            break
        else
            echo "Attempt $ATTEMPT: /vault-secrets/.env is empty or contains only comments."
        fi
    else
        echo "Attempt $ATTEMPT: Environment file /vault-secrets/.env not found."
    fi

    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "Failed to load environment variables after $MAX_ATTEMPTS attempts. Exiting..."
        exit 1
    fi

    ATTEMPT=$((ATTEMPT + 1))
    sleep $SLEEP_TIME
done

# Environment variables setup
BROKER_PROTOCOL="${BROKER_HTTP_PROTOCOL}"
BROKER_HOST="${BROKER_HTTP_HOST}"
BROKER_PORT="${BROKER_HTTP_PORT}"
BROKER_USERNAME="${BROKER_LOGIN_USERNAME}"
BROKER_PASSWORD="${BROKER_LOGIN_PASSWORD}"
VAULT_ADDR="${VAULT_ADDR}"
VAULT_TOKEN="${VAULT_ROOT_TOKEN}"

# Derived variables for Solace broker and authentication
BROKER_URL="${BROKER_PROTOCOL}://${BROKER_HOST}:${BROKER_PORT}/SEMP/v2/config"
BROKER_AUTH_HEADER="Authorization: Basic $(echo -n "${BROKER_USERNAME}:${BROKER_PASSWORD}" | base64)"
RETRY_INTERVAL_BROKER=5          # Retry interval for broker readiness checks (in seconds)
RETRY_INTERVAL_TERRAFORM=10      # Retry interval for Terraform retries (in seconds)

# Ensure mandatory environment variables are set
if [ -z "$VAULT_TOKEN" ]; then
    echo "Error: VAULT_TOKEN is not set. Please export VAULT_TOKEN before running this script."
    exit 1
fi

# Function to check Solace broker readiness
check_broker_ready() {
    wget -q --spider --header="$BROKER_AUTH_HEADER" "$BROKER_URL"
}

# Wait for Solace broker to be ready
echo "Waiting for Solace broker to be ready..."
while ! check_broker_ready; do
    echo "Broker not ready. Retrying in ${RETRY_INTERVAL_BROKER} seconds..."
    sleep $RETRY_INTERVAL_BROKER
done
echo "Solace broker is ready."

# Terraform initialization
echo "Initializing Terraform..."
if ! terraform init; then
    echo "Terraform init failed. Exiting..."
    exit 1
fi

# Plan Terraform changes
echo "Planning Terraform changes..."
if ! terraform plan -var="vault_address=$VAULT_ADDR" -var="vault_token=$VAULT_TOKEN"; then
    echo "Terraform plan failed. Exiting..."
    exit 1
fi

# Apply Terraform configuration with retries
echo "Applying Terraform configuration..."
until terraform apply -var="vault_address=$VAULT_ADDR" -var="vault_token=$VAULT_TOKEN" -auto-approve; do
    echo "Terraform apply failed. Retrying in ${RETRY_INTERVAL_TERRAFORM} seconds..."
    sleep $RETRY_INTERVAL_TERRAFORM
    echo "Re-running terraform plan to ensure state consistency..."
    terraform plan -var="vault_address=$VAULT_ADDR" -var="vault_token=$VAULT_TOKEN"
done

echo "Terraform apply completed successfully."
