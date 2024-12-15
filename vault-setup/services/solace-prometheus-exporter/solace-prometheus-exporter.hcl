auto_auth {
    method "approle" {
        config = {
            role_id_file_path = "/etc/vault-agent/shared/solace-prometheus-exporter-role_id"
            secret_id_file_path = "/etc/vault-agent/shared/solace-prometheus-exporter-secret_id"
        }
    }

    sink "file" {
        config = {
            path = "/vault/services/solace-prometheus-exporter/env/.env"
        }
    }
}

template {
    source      = "/vault/services/solace-prometheus-exporter/templates/solace-prometheus-exporter-template.tpl"
    destination = "/vault/services/solace-prometheus-exporter/env/.env"
}

vault {
    address = "http://127.0.0.1:8200"
}