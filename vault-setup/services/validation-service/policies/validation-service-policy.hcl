path "kv/validation-service/*" {
    capabilities = ["read"]
}

path "kv/message-broker/config" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/validation-service" {
    capabilities = ["read"]
}