# ------------------------------------------------------------------------------
# Terraform configuration for securely fetching secrets from HashiCorp Vault.
# These secrets are used to configure the Solace Message Broker and associated
# services such as the Aggregation and Validation Services.
# ------------------------------------------------------------------------------

data "vault_generic_secret" "message_broker_config" {
    path = "kv/message-broker/config"
}

data "vault_generic_secret" "message_broker_aggregation_service_config" {
    path = "kv/message-broker/config/aggregation-service"
}

data "vault_generic_secret" "message_broker_otel_creds" {
    path = "kv/message-broker/creds/otel"
}

data "vault_generic_secret" "message_broker_otel_config" {
    path = "kv/message-broker/config/otel"
}

data "vault_generic_secret" "message_broker_validation_service_creds" {
    path = "kv/message-broker/creds/validation-service"
}

data "vault_generic_secret" "message_broker_aggregation_service_creds" {
    path = "kv/message-broker/creds/aggregation-service"
}

data "vault_generic_secret" "message_broker_login_creds" {
    path = "kv/message-broker/creds/login"
}
