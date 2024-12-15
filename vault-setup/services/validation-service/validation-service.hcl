# ------------------------------------------------------------------------------
# Vault Agent Configuration
# This configuration enables auto-authentication for the validation service using
# the AppRole method. It defines a file sink for writing secrets as environment
# variables, specifies a template for rendering environment variables, and sets
# the Vault server address for communication.
# ------------------------------------------------------------------------------

auto_auth {
    method "approle" {
        config = {
            role_id_file_path = "/etc/vault-agent/shared/validation-service-role_id"
            secret_id_file_path = "/etc/vault-agent/shared/validation-service-secret_id"
        }
    }

    sink "file" {
        config = {
            path = "/vault/services/validation-service/env/.env"
        }
    }
}

template {
    source      = "/vault/services/validation-service/templates/validation-service-template.tpl"
    destination = "/vault/services/validation-service/env/.env"
}

vault {
    address = "http://127.0.0.1:8200"
}
