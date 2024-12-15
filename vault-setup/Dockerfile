# ------------------------------------------------------------------------------
# Dockerfile for Vault Server with Setup Scripts
# This Dockerfile uses the official HashiCorp Vault image, installs necessary 
# dependencies, and copies setup scripts for Vault initialization and configuration.
# ------------------------------------------------------------------------------

# Base image
FROM hashicorp/vault:latest

# Install additional dependencies: curl and jq
RUN apk add --no-cache curl jq

# Copy setup scripts to the Vault container
COPY setup /vault/setup
