#!/bin/sh

# Set configuration directory
CONFIG_DIR="./vault/config"

# Start Vault server in the foreground and background the initialization script
echo "Starting Vault server in the foreground..."
sh /vault/setup/init_agent.sh &

vault server -config="$CONFIG_DIR/vault-config.hcl"
