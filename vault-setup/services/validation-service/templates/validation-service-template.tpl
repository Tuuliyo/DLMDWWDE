BROKER_HOST="{{ with secret "kv/message-broker/config" }}{{ .Data.smf_host }}{{ end }}"
BROKER_PORT="{{ with secret "kv/message-broker/config" }}{{ .Data.smf_port }}{{ end }}"
BROKER_PROTOCOL="{{ with secret "kv/message-broker/config" }}{{ .Data.smf_protocol }}{{ end }}"
BROKER_MSG_VPN="{{ with secret "kv/message-broker/config" }}{{ .Data.msg_vpn }}{{ end }}"
BROKER_SMF_USERNAME="{{ with secret "kv/message-broker/creds/validation-service" }}{{ .Data.username }}{{ end }}"
BROKER_SMF_PASSWORD="{{ with secret "kv/message-broker/creds/validation-service" }}{{ .Data.password }}{{ end }}"
BROKER_POS_TOPIC_PREFIX="{{ with secret "kv/message-broker/config" }}{{ .Data.pos_topic_prefix }}{{ end }}"

POS_SERVICE_USERNAME="{{ with secret "kv/validation-service/creds/pos-service" }}{{ .Data.username }}{{ end }}"
POS_SERVICE_PASSWORD="{{ with secret "kv/validation-service/creds/pos-service" }}{{ .Data.password }}{{ end }}"

AGGREGATION_SERVICE_USERNAME="{{ with secret "kv/validation-service/creds/aggregation-service" }}{{ .Data.username }}{{ end }}"
AGGREGATION_SERVICE_PASSWORD="{{ with secret "kv/validation-service/creds/aggregation-service" }}{{ .Data.password }}{{ end }}"