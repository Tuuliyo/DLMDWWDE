#!/bin/sh

# Set variables
VAULT_DATA_DIR="./vault/data"
VAULT_ADDR="http://127.0.0.1:8200"
SHARED_DIR="/etc/vault-agent/shared"
SERVICES="pos-service"

# Export VAULT_ADDR globally
export VAULT_ADDR="$VAULT_ADDR"

# Ensure necessary directories exist
echo "Creating necessary directories..."
mkdir -p "$SHARED_DIR"

# Initialize Vault and save unseal keys
echo "Initializing Vault..."
vault operator init -format=json > init.json || { echo "Failed to initialize Vault."; exit 1; }

# Extract unseal keys and root token
UNSEAL_KEYS=$(jq -r ".unseal_keys_b64[]" init.json)
ROOT_TOKEN=$(jq -r ".root_token" init.json)
echo "Vault initialized. Root token and unseal keys saved to 'init.json'."

# Unseal Vault
echo "Unsealing Vault..."
for KEY in $UNSEAL_KEYS; do
  vault operator unseal "$KEY" || { echo "Error unsealing Vault with key: $KEY"; exit 1; }
done

# Check if Vault is unsealed
SEALED=$(vault status -format=json | jq -r ".sealed")
if [ "$SEALED" = "true" ]; then
  echo "Vault is still sealed after unsealing attempt."
  exit 1
fi

# Authenticate with root token
export VAULT_TOKEN=$ROOT_TOKEN

# Enable AppRole authentication
echo "Enabling AppRole authentication..."
vault auth enable approle || { echo "Failed to enable AppRole authentication."; exit 1; }

# Enable KV secrets engine
echo "Enabling KV secrets engine at path 'kv'..."
vault secrets enable -path=kv kv || echo "KV engine already enabled."

# Loop through each service to set up policies and roles
for SERVICE in $SERVICES; do
  SERVICE_DIR="/vault/${SERVICE}"
  POLICY_FILE="${SERVICE_DIR}/policies/${SERVICE}-policy.hcl"
  ROLE_NAME="${SERVICE}-role"
  ROLE_ID_FILE="$SHARED_DIR/${SERVICE}-role_id"
  SECRET_ID_FILE="$SHARED_DIR/${SERVICE}-secret_id"
  SECRETS_SCRIPT="$SERVICE_DIR/${SERVICE}.sh"

  echo "Setting up Vault policy and AppRole for ${SERVICE}..."

  # Write the policy using the HCL file
  echo "Writing policy for ${SERVICE}..."
  vault policy write ${SERVICE}-policy "$POLICY_FILE" || { echo "Failed to write policy for ${SERVICE}."; exit 1; }

  # Create the AppRole
  echo "Creating AppRole for ${SERVICE}..."
  vault write auth/approle/role/${ROLE_NAME} \
      token_policies="${SERVICE}-policy" \
      secret_id_ttl=0 \
      token_ttl=1h \
      token_max_ttl=4h || { echo "Failed to create AppRole for ${SERVICE}."; exit 1; }

  # Fetch Role ID and Secret ID
  echo "Fetching Role ID and Secret ID for ${SERVICE}..."
  ROLE_ID=$(vault read -field=role_id auth/approle/role/${ROLE_NAME}/role-id) || { echo "Failed to fetch Role ID for ${SERVICE}."; exit 1; }
  SECRET_ID=$(vault write -field=secret_id -f auth/approle/role/${ROLE_NAME}/secret-id) || { echo "Failed to fetch Secret ID for ${SERVICE}."; exit 1; }

  # Save Role ID and Secret ID
  echo "Saving Role ID and Secret ID for ${SERVICE}..."
  echo "$ROLE_ID" > $ROLE_ID_FILE
  echo "$SECRET_ID" > $SECRET_ID_FILE
  chmod 600 $ROLE_ID_FILE $SECRET_ID_FILE

  # Run service-specific script to populate secrets
  if [ -f "$SECRETS_SCRIPT" ]; then
    echo "Running secrets setup script for ${SERVICE}..."
    sh "$SECRETS_SCRIPT" || { echo "Failed to populate secrets for ${SERVICE}."; exit 1; }
  else
    echo "No secrets setup script found for ${SERVICE}. Skipping..."
  fi

  echo "${SERVICE} setup completed."
done

# Start Vault Agent for each service
for SERVICE in $SERVICES; do
  echo "Starting Vault Agent for ${SERVICE}..."
  nohup vault agent -config="/vault/${SERVICE}/${SERVICE}.hcl" > "agent-${SERVICE}.log" 2>&1 &
  echo "Vault Agent for ${SERVICE} started."
done

# Wait for agents to stabilize
sleep 5

echo "Vault and Vault Agents setup completed successfully."

# Print Vault status
vault status

# Print final instructions
echo "Vault server and Vault Agents setup completed."
echo "Press Ctrl+C to stop the container."

# Keep the container alive
tail -f /dev/null