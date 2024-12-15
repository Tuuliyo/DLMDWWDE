#!/bin/sh

# Set configuration directory
CONFIG_DIR="./vault/config"

# Start Vault server in the foreground and background the initialization script
echo "Starting Vault server in the foreground..."

vault server -config="$CONFIG_DIR/vault-config.hcl" &
sleep 5
sh /vault/setup/init_agent.sh
