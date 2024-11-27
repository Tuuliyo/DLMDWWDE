import logging
import time
from solace_consumer import SolaceConsumer

# Solace configuration
POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": "tcp://message-broker:55555",
    "solace.messaging.service.vpn-name": "default",
    "solace.messaging.authentication.scheme.basic.username": "sale.pos.transaction.aggregation",
    "solace.messaging.authentication.scheme.basic.password": "Test1234",
}
POS_QUEUE_NAME = "sale.pos.transaction.aggregation.service"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = SolaceConsumer(POS_TRANSACTION_CONFIG, POS_QUEUE_NAME)
    
    try:
        logging.info("Solace consumer started. Waiting for messages...")
        while True:
            time.sleep(1)  # Keep the consumer running
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
        consumer.shutdown()
