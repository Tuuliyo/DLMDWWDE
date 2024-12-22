# ------------------------------------------------------------------------------
# Vault Policy Configuration
# This configuration defines access permissions for reading secrets related to
# the message broker configuration and OpenTelemetry credentials stored in the
# KV secrets engine.
# ------------------------------------------------------------------------------

path "kv/otel-collector/config" {
    capabilities = ["read"]
}

path "kv/message-broker/config" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/otel" {
    capabilities = ["read"]
}
