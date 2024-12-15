#!/bin/sh

# ------------------------------------------------------------------------------
# Script to Start Vault Server and Initialize Agent
# This script starts the Vault server in the foreground using a specified
# configuration file and initializes the Vault agent with a setup script.
# ------------------------------------------------------------------------------

# Set the directory containing the Vault server configuration
CONFIG_DIR="./vault/config"

# Start the Vault server in the foreground
echo "Starting Vault server with configuration from $CONFIG_DIR..."
vault server -config="$CONFIG_DIR/vault-config.hcl" &

# Allow the Vault server to start
sleep 5

# Run the Vault agent initialization script
echo "Initializing Vault agent..."
sh /vault/setup/init_agent.sh
