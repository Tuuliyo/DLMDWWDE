# DLMDWWDE
University Project for Data Engineering - POS real-time integration

Inital Test

# Vault structure for all services and shared configurations
kv/
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
├── __aggregation-service/ -> read-only__ 
├── __pos-service/ -> read-only__
├── __otel-collector/ -> read-only__
