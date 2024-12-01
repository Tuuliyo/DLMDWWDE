
terraform {
    required_providers {
        solacebroker = {
        source = "registry.terraform.io/solaceproducts/solacebroker"
        }
    }
}

provider "solacebroker" {
    username = var.solace_username
    password = var.solace_password
    url = var.solace_broker
}