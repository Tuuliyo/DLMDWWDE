# ------------------------------------------------------------------------------
# Vault Policy Configuration
# This configuration defines the paths and permissions for accessing secrets
# related to the message broker and services (e.g., aggregation and validation services).
# ------------------------------------------------------------------------------

path "kv/message-broker/config" {
    capabilities = ["read"]
}

path "kv/message-broker/config/aggregation-service" {
    capabilities = ["read"]
}

path "kv/validation-service/config" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/aggregation-service" {
    capabilities = ["read"]
}

path "kv/validation-service/creds/aggregation-service" {
    capabilities = ["read"]
}

path "kv/otel-collector/config" {
    capabilities = ["read"]
}
