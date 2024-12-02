resource "solacebroker_msg_vpn_telemetry_profile" "otel" {
    msg_vpn_name = var.solace_vpn_name
    telemetry_profile_name = "otel"
    receiver_enabled = true
    trace_enabled = true
    trace_send_span_generation_enabled = true
    receiver_acl_connect_default_action = "allow"
}

resource "solacebroker_msg_vpn_telemetry_profile_trace_filter" "traces" {
    msg_vpn_name = var.solace_vpn_name
    telemetry_profile_name = solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name
    trace_filter_name = "full_traces"
    enabled = true
}

resource "solacebroker_msg_vpn_telemetry_profile_trace_filter_subscription" "all" {
    msg_vpn_name = var.solace_vpn_name
    subscription= ">"
    subscription_syntax = "smf"
    telemetry_profile_name = solacebroker_msg_vpn_telemetry_profile.otel.telemetry_profile_name
    trace_filter_name = solacebroker_msg_vpn_telemetry_profile_trace_filter.traces.trace_filter_name
}

