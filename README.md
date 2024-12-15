# DLMDWWDE
University Project for Data Engineering - POS real-time integration

Inital Test

# Vault structure for all services and shared configurations
dev/
├── vault-service/
│   ├── config/
│   │   ├── vault_addr
│   │   ├── api_addr
│   ├── creds/
│       ├── token/
│       │   ├── root_token
├── message-broker/
│   ├── config/
│   │   ├── http_host
│   │   ├── http_port
│   │   ├── http_protocol
│   │   ├── smf_host
│   │   ├── smf_port
│   │   ├── smf_protocol
│   │   ├── health_host
│   │   ├── health_port
│   │   ├── health_protocol
│   │   ├── amqp_host
│   │   ├── amqp_port
│   │   ├── msg_vpn
│   │   ├── pos_topic_prefix
│   │   ├── aggregation-service/
│   │   │   ├── queue_name
│   ├── creds/
│       ├── login/
│       │   ├── username
│       │   ├── password
│       ├── otel/
│       │   ├── username
│       │   ├── password
│       ├── validation-service/
│       │   ├── username
│       │   ├── password
│       ├── aggregation-service/
│       │   ├── username
│       │   ├── password
├── validation-service/
│   ├── config/
│       ├── api_protocol
│       ├── api_host
│       ├── api_port
│   ├── creds/
│       ├── aggregation-service/
│       │   ├── username
│       │   ├── password
│       ├── pos-service/
│       │   ├── username
│       │   ├── password
├── solace-prometheus-exporter/
│   ├── config/
│   │   ├── listen_addr_host
│   │   ├── listen_addr_port
│   │   ├── timeout
│   │   ├── ssl_verify
│   │   ├── listen_tls
├── __aggregation-service/__
├── __pos-service/__
├── __otel-collector/__
