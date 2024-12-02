resource "solacebroker_msg_vpn_client_username" "validation_service" {
    client_username = "sale_pos_transaction_validation"
    msg_vpn_name = var.solace_vpn_name
    password = "Validation1234!"
    client_profile_name = solacebroker_msg_vpn_client_profile.validation_service.client_profile_name
    acl_profile_name = solacebroker_msg_vpn_acl_profile.validation_service.acl_profile_name
    enabled = true
    subscription_manager_enabled = true
    guaranteed_endpoint_permission_override_enabled = true
}

resource "solacebroker_msg_vpn_client_username" "aggregation_service" {
    client_username = "sale_pos_transaction_aggregation"
    msg_vpn_name = var.solace_vpn_name
    password = "Aggregation1234!"
    client_profile_name = solacebroker_msg_vpn_client_profile.aggregation_service.client_profile_name
    acl_profile_name = solacebroker_msg_vpn_acl_profile.aggregation_service.acl_profile_name
    enabled = true
    subscription_manager_enabled = true
    guaranteed_endpoint_permission_override_enabled = true
}

resource "solacebroker_msg_vpn_client_username" "telemetry" {
    client_username = "telemetry_collector_service"
    msg_vpn_name = var.solace_vpn_name
    password = "Telemetry1234!"
    client_profile_name = "#telemetry-${solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name}" 
    acl_profile_name = "#telemetry-${solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name}"
    enabled = true
    subscription_manager_enabled = true
    guaranteed_endpoint_permission_override_enabled = true
}