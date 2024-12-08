BROKER_HOST="{{ with secret "kv/aggregation-service" }}{{ .Data.broker_host }}{{ end }}"
BROKER_HEALTH_PORT="{{ with secret "kv/aggregation-service" }}{{ .Data.broker_health_port }}{{ end }}"
BROKER_HEALTH_PROTOCOL="{{ with secret "kv/aggregation-service" }}{{ .Data.broker_health_protocol }}{{ end }}"
BROKER_MSG_VPN="{{ with secret "kv/aggregation-service" }}{{ .Data.broker_msg_vpn }}{{ end }}"
BROKER_MSG_PORT="{{ with secret "kv/aggregation-service" }}{{ .Data.broker_port }}{{ end }}"
BROKER_MSG_PROTOCOL="{{ with secret "kv/aggregation-service" }}{{ .Data.broker_protocol }}{{ end }}"
API_HOST="{{ with secret "kv/aggregation-service" }}{{ .Data.api_host }}{{ end }}"
API_PORT="{{ with secret "kv/aggregation-service" }}{{ .Data.api_port }}{{ end }}"
API_PROTOCOL="{{ with secret "kv/aggregation-service" }}{{ .Data.api_protocol }}{{ end }}"