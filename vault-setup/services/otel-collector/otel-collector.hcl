# ------------------------------------------------------------------------------
# Vault Agent Configuration
# This configuration defines the setup for auto-authentication using the AppRole
# method, specifies a file sink for injecting secrets as environment variables,
# configures template rendering for environment variables, and sets the Vault server address.
# ------------------------------------------------------------------------------

auto_auth {
    method "approle" {
        config = {
            role_id_file_path = "/etc/vault-agent/shared/otel-collector-role_id"
            secret_id_file_path = "/etc/vault-agent/shared/otel-collector-secret_id"
        }
    }

    sink "file" {
        config = {
            path = "/vault/services/otel-collector/env/.env"
        }
    }
}

template {
    source      = "/vault/services/otel-collector/templates/otel-collector-template.tpl"
    destination = "/vault/services/otel-collector/env/.env"
}

vault {
    address = "http://127.0.0.1:8200"
}
