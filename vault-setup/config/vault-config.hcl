storage "file" {
    path = "./data"
}

listener "tcp" {
    address     = "0.0.0.0:8200"
    tls_disable = true
}

disable_mlock = true
ui = true
api_addr = "http://0.0.0.0:8200"