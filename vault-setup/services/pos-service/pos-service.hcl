auto_auth {
    method "approle" {
        config = {
            role_id_file_path = "/etc/vault-agent/shared/pos-service-role_id"
            secret_id_file_path = "/etc/vault-agent/shared/pos-service-secret_id"
        }
    }

    sink "file" {
        config = {
            path = "/vault/services/pos-service/env/.env"
        }
    }
}

template {
    source      = "/vault/services/pos-service/templates/pos-service-template.tpl"
    destination = "/vault/services/pos-service/env/.env"
}

vault {
    address = "http://127.0.0.1:8200"
}