BROKER_HOST="{{ with secret "kv/validation-service" }}{{ .Data.broker_host }}{{ end }}"
BROKER_PORT="{{ with secret "kv/validation-service" }}{{ .Data.broker_port }}{{ end }}"
BROKER_PROTOCOL="{{ with secret "kv/validation-service" }}{{ .Data.broker_protocol }}{{ end }}"
BROKER_MSG_VPN="{{ with secret "kv/validation-service" }}{{ .Data.broker_msg_vpn }}{{ end }}"