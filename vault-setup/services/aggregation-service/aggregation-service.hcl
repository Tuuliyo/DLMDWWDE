auto_auth {
    method "approle" {
        config = {
            role_id_file_path = "/etc/vault-agent/shared/aggregation-service-role_id"
            secret_id_file_path = "/etc/vault-agent/shared/aggregation-service-secret_id"
        }
    }

    sink "file" {
        config = {
            path = "/vault/services/aggregation-service/env/.env"
        }
    }
}

template {
    source      = "/vault/services/aggregation-service/templates/aggregation-service-template.tpl"
    destination = "/vault/services/aggregation-service/env/.env"
}

vault {
    address = "http://127.0.0.1:8200"
}