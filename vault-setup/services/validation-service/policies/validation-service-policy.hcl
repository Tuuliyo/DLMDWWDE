# ------------------------------------------------------------------------------
# Vault Policy Configuration
# This configuration grants read access to secrets stored in the KV secrets engine
# for the validation service and the message broker. It includes access to the
# validation service configuration, message broker settings, and validation service
# credentials within the message broker.
# ------------------------------------------------------------------------------

path "kv/validation-service/*" {
    capabilities = ["read"]
}

path "kv/message-broker/config" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/validation-service" {
    capabilities = ["read"]
}
