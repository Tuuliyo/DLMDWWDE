auto_auth {
    method "approle" {
        config = {
            role_id_file_path = "/etc/vault-agent/shared/message-broker-role_id"
            secret_id_file_path = "/etc/vault-agent/shared/message-broker-secret_id"
        }
    }

    sink "file" {
        config = {
            path = "/vault/services/message-broker/env/.env"
        }
    }
}

template {
    source      = "/vault/services/message-broker/templates/message-broker-template.tpl"
    destination = "/vault/services/message-broker/env/.env"
}

vault {
    address = "http://127.0.0.1:8200"
}