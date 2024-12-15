# ------------------------------------------------------------------------------
# Terraform configuration for setting up OpenTelemetry (OTel) telemetry profiles 
# in Solace Message Broker. This includes:
# - A telemetry profile for trace collection.
# - A trace filter for full traces.
# - A subscription for the trace filter.
# ------------------------------------------------------------------------------

resource "solacebroker_msg_vpn_telemetry_profile" "otel" {
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    telemetry_profile_name = "otel"
    receiver_enabled = true
    trace_enabled = true
    trace_send_span_generation_enabled = true
    receiver_acl_connect_default_action = "allow"
}

resource "solacebroker_msg_vpn_telemetry_profile_trace_filter" "traces" {
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    telemetry_profile_name = solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name
    trace_filter_name = "full_traces"
    enabled = true
}

resource "solacebroker_msg_vpn_telemetry_profile_trace_filter_subscription" "all" {
    msg_vpn_name = data.vault_generic_secret.message_broker_config.data["msg_vpn"]
    subscription = ">"
    subscription_syntax = "smf"
    telemetry_profile_name = solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name
    trace_filter_name = solacebroker_msg_vpn_telemetry_profile_trace_filter.traces.trace_filter_name
}
