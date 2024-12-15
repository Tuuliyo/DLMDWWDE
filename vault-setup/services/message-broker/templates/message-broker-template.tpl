VAULT_ADDR="{{ with secret "kv/vault-service/config" }}{{ .Data.vault_addr }}{{ end }}"
VAULT_ROOT_TOKEN="{{ with secret "kv/vault-service/creds/token" }}{{ .Data.root_token }}{{ end }}"

BROKER_HTTP_PORT="{{ with secret "kv/message-broker/config" }}{{ .Data.http_port }}{{ end }}"
BROKER_HTTP_HOST="{{ with secret "kv/message-broker/config" }}{{ .Data.http_host }}{{ end }}"
BROKER_HTTP_PROTOCOL="{{ with secret "kv/message-broker/config" }}{{ .Data.http_protocol }}{{ end }}"

BROKER_LOGIN_USERNAME="{{ with secret "kv/message-broker/creds/login" }}{{ .Data.username }}{{ end }}"
BROKER_LOGIN_PASSWORD="{{ with secret "kv/message-broker/creds/login" }}{{ .Data.password }}{{ end }}"