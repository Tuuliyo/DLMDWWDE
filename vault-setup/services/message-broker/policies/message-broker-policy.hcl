# ------------------------------------------------------------------------------
# Vault Policy Configuration
# This configuration defines access permissions for reading secrets in the KV
# engine, including message broker configurations, credentials, and Vault service settings.
# ------------------------------------------------------------------------------

path "kv/message-broker/*" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/login" {
    capabilities = ["read"]
}

path "kv/vault-service/*" {
    capabilities = ["read"]
}
