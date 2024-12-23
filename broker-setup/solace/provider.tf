# ------------------------------------------------------------------------------
# Terraform configuration for providers used in the Solace Message Broker setup.
# This configuration includes the Vault provider for securely fetching secrets
# and the SolaceBroker provider for managing broker resources.
# ------------------------------------------------------------------------------

terraform {
    required_providers {
        solacebroker = {
            source = "registry.terraform.io/solaceproducts/solacebroker"
        }
        vault = {
            source  = "hashicorp/vault"
            version = ">=3.0.0"
        }
    }
}

provider "vault" {
    address = var.vault_address
    token   = var.vault_token
}

provider "solacebroker" {
    username = data.vault_generic_secret.message_broker_login_creds.data["username"]
    password = data.vault_generic_secret.message_broker_login_creds.data["password"]
    url      = "${data.vault_generic_secret.message_broker_config.data["http_protocol"]}://${data.vault_generic_secret.message_broker_config.data["http_host"]}:${data.vault_generic_secret.message_broker_config.data["http_port"]}"
}
