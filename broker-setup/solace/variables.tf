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
    type    = number
    default = 10
}