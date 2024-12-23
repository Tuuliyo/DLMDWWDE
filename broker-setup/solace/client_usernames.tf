# ------------------------------------------------------------------------------
# Terraform configuration for creating client usernames in Solace Message Broker.
# Client usernames define the credentials and permissions for services interacting
# with the broker, such as Validation Service, Aggregation Service, and Telemetry.
# ------------------------------------------------------------------------------

resource "solacebroker_msg_vpn_client_username" "validation_service" {
    client_username = data.vault_generic_secret.message_broker_validation_service_creds.data["username"]
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    password = data.vault_generic_secret.message_broker_validation_service_creds.data["password"]
    client_profile_name = solacebroker_msg_vpn_client_profile.validation_service.client_profile_name
    acl_profile_name = solacebroker_msg_vpn_acl_profile.validation_service.acl_profile_name
    enabled = true
    subscription_manager_enabled = true
    guaranteed_endpoint_permission_override_enabled = true
}

resource "solacebroker_msg_vpn_client_username" "aggregation_service" {
    client_username = data.vault_generic_secret.message_broker_aggregation_service_creds.data["username"]
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    password = data.vault_generic_secret.message_broker_aggregation_service_creds.data["password"]
    client_profile_name = solacebroker_msg_vpn_client_profile.aggregation_service.client_profile_name
    acl_profile_name = solacebroker_msg_vpn_acl_profile.aggregation_service.acl_profile_name
    enabled = true
    subscription_manager_enabled = true
    guaranteed_endpoint_permission_override_enabled = true
}

resource "solacebroker_msg_vpn_client_username" "telemetry" {
    client_username = data.vault_generic_secret.message_broker_otel_creds.data["username"]
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    password = data.vault_generic_secret.message_broker_otel_creds.data["password"]
    client_profile_name = "#telemetry-${solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name}"
    acl_profile_name = "#telemetry-${solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name}"
    enabled = true
    subscription_manager_enabled = true
    guaranteed_endpoint_permission_override_enabled = true
}
