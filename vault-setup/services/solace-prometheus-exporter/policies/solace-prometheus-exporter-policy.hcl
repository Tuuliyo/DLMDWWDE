path "kv/solace-prometheus-exporter/*" {
    capabilities = ["read"]
}

path "kv/message-broker/config" {
    capabilities = ["read"]
}

path "kv/message-broker/creds/login" {
    capabilities = ["read"]
}