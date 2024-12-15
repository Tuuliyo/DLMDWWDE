path "kv/message-broker/*" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/login" {
    capabilities = ["read"]
}

path "kv/vault-service/*" {
    capabilities = ["read"]
}