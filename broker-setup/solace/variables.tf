# ------------------------------------------------------------------------------
# Terraform variable definitions for the Solace Message Broker configuration.
# These variables include:
# - Vault server details for secret management.
# - The number of stores for which queues and subscriptions are created.
# ------------------------------------------------------------------------------

variable "vault_address" {
    description = "Vault server address"
    default     = "http://vault:8200"
}

variable "vault_token" {
    description = "Vault authentication token"
    sensitive   = true
    default     = ""
}

variable "number_of_stores" {
    type        = number
    description = "Number of stores for which queues and subscriptions will be created"
    default     = 10
}
