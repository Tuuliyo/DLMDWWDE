resource "solacebroker_msg_vpn_client_profile" "validation_service" {
    client_profile_name = "sale_pos_transaction_validation"
    msg_vpn_name = var.solace_vpn_name
    allow_guaranteed_msg_send_enabled = true
}

resource "solacebroker_msg_vpn_client_profile" "aggregation_service" {
    client_profile_name = "sale_pos_transaction_aggregation"
    msg_vpn_name = var.solace_vpn_name
    allow_guaranteed_msg_receive_enabled = true
    allow_guaranteed_endpoint_create_enabled = true
}