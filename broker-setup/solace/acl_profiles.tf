resource "solacebroker_msg_vpn_acl_profile" "aggregation_service" {
    acl_profile_name = "sale_pos_transaction_aggregation"
    msg_vpn_name = var.solace_vpn_name
    publish_topic_default_action = "disallow"
    client_connect_default_action = "allow"
}

resource "solacebroker_msg_vpn_acl_profile" "validation_service" {
    acl_profile_name = "sale_pos_transaction_validation"
    msg_vpn_name = var.solace_vpn_name
    publish_topic_default_action = "allow"
    client_connect_default_action = "allow"
}