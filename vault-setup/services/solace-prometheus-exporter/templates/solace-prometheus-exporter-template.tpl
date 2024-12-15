SOLACE_USERNAME={{ with secret "kv/message-broker/creds/login" }}{{ .Data.username }}{{ end }}
SOLACE_PASSWORD={{ with secret "kv/message-broker/creds/login" }}{{ .Data.password }}{{ end }}

SOLACE_DEFAULT_VPN={{ with secret "kv/message-broker/config" }}{{ .Data.msg_vpn }}{{ end }}
SOLACE_SCRAPE_URI={{ with secret "kv/message-broker/config" }}{{ .Data.http_protocol }}://{{ .Data.http_host }}:{{ .Data.http_port }}{{ end }}
SOLACE_LISTEN_ADDR={{ with secret "kv/solace-prometheus-exporter/config" }}{{ .Data.listen_addr_host }}:{{ .Data.listen_addr_port }}{{ end }}

SOLACE_TIMEOUT={{ with secret "kv/solace-prometheus-exporter/config" }}{{ .Data.timeout }}{{ end }}
SOLACE_SSL_VERIFY={{ with secret "kv/solace-prometheus-exporter/config" }}{{ .Data.ssl_verify }}{{ end }}
SOLACE_LISTEN_TLS={{ with secret "kv/solace-prometheus-exporter/config" }}{{ .Data.listen_tls }}{{ end }}