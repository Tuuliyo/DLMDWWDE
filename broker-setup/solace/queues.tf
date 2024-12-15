# ------------------------------------------------------------------------------
# Terraform configuration for creating queues and subscriptions in Solace Message Broker.
# This setup includes:
# - A queue for receipt messages with a corresponding subscription.
# - Per-store queues and subscriptions for aggregations.
# ------------------------------------------------------------------------------

resource "solacebroker_msg_vpn_queue" "receipts_queue" {
    queue_name   = data.vault_generic_secret.message_broker_aggregation_service_config.data["queue_name"]
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    access_type  = "exclusive"
    egress_enabled = true
    ingress_enabled = true
    owner          = solacebroker_msg_vpn_client_username.aggregation_service.client_username
    permission     = "no-access"
}

resource "solacebroker_msg_vpn_queue_subscription" "receipts_subscription" {
    queue_name        = solacebroker_msg_vpn_queue.receipts_queue.queue_name
    msg_vpn_name      = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    subscription_topic = "${data.vault_generic_secret.message_broker_config.data["pos_topic_prefix"]}/receipt/>"
}

resource "solacebroker_msg_vpn_queue" "store_queue" {
    count = var.number_of_stores

    queue_name   = "sale_pos_transaction_aggregations_store${count.index + 1}.q"
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    access_type  = "exclusive"
    ingress_enabled = true
    permission      = "no-access"
}

resource "solacebroker_msg_vpn_queue_subscription" "store_subscription" {
    count = var.number_of_stores

    queue_name        = solacebroker_msg_vpn_queue.store_queue[count.index].queue_name
    msg_vpn_name      = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    subscription_topic = "${data.vault_generic_secret.message_broker_config.data["pos_topic_prefix"]}/aggregations/STORE_${count.index + 1}/>"
}
