API_HOST="{{ with secret "kv/validation-service/config" }}{{ .Data.api_host }}{{ end }}"
API_PORT="{{ with secret "kv/validation-service/config" }}{{ .Data.api_port }}{{ end }}"
API_PROTOCOL="{{ with secret "kv/validation-service/config" }}{{ .Data.api_protocol }}{{ end }}"

API_USERNAME="{{ with secret "kv/validation-service/creds/pos-service" }}{{ .Data.username }}{{ end }}"
API_PASSWORD="{{ with secret "kv/validation-service/creds/pos-service" }}{{ .Data.password }}{{ end }}"

BROKER_HOST="{{ with secret "kv/message-broker/config" }}{{ .Data.health_host }}{{ end }}"
BROKER_PORT="{{ with secret "kv/message-broker/config" }}{{ .Data.health_port }}{{ end }}"
BROKER_PROTOCOL="{{ with secret "kv/message-broker/config" }}{{ .Data.health_protocol }}{{ end }}"