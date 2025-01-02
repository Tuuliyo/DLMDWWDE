BROKER_AMQP_HOST="{{ with secret "kv/message-broker/config" }}{{ .Data.amqp_host }}{{ end }}"
BROKER_AMQP_PORT="{{ with secret "kv/message-broker/config" }}{{ .Data.amqp_port }}{{ end }}"

BROKER_OTEL_USERNAME="{{ with secret "kv/message-broker/creds/otel" }}{{ .Data.username }}{{ end }}"
BROKER_OTEL_PASSWORD="{{ with secret "kv/message-broker/creds/otel" }}{{ .Data.password }}{{ end }}"
BROKER_OTEL_QUEUE_NAME="{{ with secret "kv/message-broker/config/otel" }}{{ .Data.queue_name }}{{ end }}"

TEMPO_HOST="{{ with secret "kv/otel-collector/config" }}{{ .Data.tempo_host }}{{ end }}"
TEMPO_PORT="{{ with secret "kv/otel-collector/config" }}{{ .Data.tempo_port }}{{ end }}"