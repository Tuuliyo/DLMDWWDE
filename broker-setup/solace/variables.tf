
variable "solace_username" {
    description = "Solace broker admin username"
    type        = string
}

variable "solace_password" {
    description = "Solace broker admin password"
    type        = string
    sensitive   = true
}

variable "solace_broker" {
    description = "Solace broker URL or IP"
    type        = string
}

variable "solace_vpn_name" {
    description = "Solace Message VPN name"
    type        = string
}

variable "number_of_stores" {
    type    = number
    default = 10
}