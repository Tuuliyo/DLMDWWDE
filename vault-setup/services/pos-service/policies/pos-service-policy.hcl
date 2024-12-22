# ------------------------------------------------------------------------------
# Vault Policy Configuration
# This configuration defines access permissions for reading secrets in the KV
# secrets engine, including settings and credentials for the message broker and
# validation service.
# ------------------------------------------------------------------------------

path "kv/otel-collector/config" {
    capabilities = ["read"]
}

path "kv/message-broker/config" {
    capabilities = ["read"]
}

path "kv/validation-service/config" {
    capabilities = ["read"]
}

path "kv/validation-service/creds/pos-service" {
    capabilities = ["read"]
}
