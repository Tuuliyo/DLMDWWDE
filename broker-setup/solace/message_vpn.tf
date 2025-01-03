# ------------------------------------------------------------------------------
# Terraform configuration for creating and enabling a Solace Message VPN.
# A Message VPN (Virtual Private Network) isolates message traffic between
# services and defines authentication, spool usage, and protocol services.
# ------------------------------------------------------------------------------

# Message VPN configuration
resource "solacebroker_msg_vpn" "basic_enable" {
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    alias = "pos-simulation"
    authentication_basic_enabled = true
    authentication_basic_type = "internal"
    enabled = true
    max_msg_spool_usage = 10000
    service_amqp_plain_text_enabled = true
    service_amqp_plain_text_listen_port = 5672
    service_amqp_tls_enabled = true
    service_amqp_tls_listen_port = 5671
}
