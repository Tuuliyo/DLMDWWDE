from opentelemetry import trace
from models.transaction_event import Transaction
from models.aggregated_event import AggregatedEvent
from solace_publisher import SolacePublisher
from logger_config import setup_logger

# Initialize logger
logger = setup_logger()

# Configuration for the SolacePublisher to publish POS transactions
POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": "tcp://message-broker:55555",
    "solace.messaging.service.vpn-name": "default",
    "solace.messaging.authentication.scheme.basic.username": "testuser",
    "solace.messaging.authentication.scheme.basic.password": "Test1234!",
}
# Setup topic root for POS transactions
POS_TOPIC_PREFIX = "sale/pos/transaction"

# Initialize the SolacePublisher for POS transactions
POS_PUBLISHER = SolacePublisher(config=POS_TRANSACTION_CONFIG)


async def correct_transaction(transaction: Transaction):
    """
    Simulate more complex transaction corrections with OpenTelemetry tracing.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("correct_transaction") as span:
        span.set_attribute("transaction.id", str(transaction.transaction_id))
        span.set_attribute("transaction.store_id", transaction.store_id)
        span.set_attribute("transaction.total_amount", transaction.total_amount)

        calculated_total = sum(item.total_price for item in transaction.items)
        if calculated_total != transaction.total_amount:
            transaction.total_amount = round(calculated_total, 2)
            span.set_attribute("transaction.corrected_total", transaction.total_amount)
            logger.info(
                f"Corrected total for transaction {transaction.transaction_id}: {transaction.total_amount}"
            )

        if transaction.payment_status != "success":
            span.set_attribute("transaction.payment_status", "failed")
            logger.warning(
                f"Transaction {transaction.transaction_id} failed payment validation."
            )
        else:
            span.set_attribute("transaction.payment_status", "success")
            topic = (
                f"{POS_TOPIC_PREFIX}/receipt/{transaction.store_id}/{transaction.cashier_id}/{transaction.payment_method}/"
                f"{transaction.payment_status}/{transaction.timestamp}/{transaction.transaction_id}/"
                f"{transaction.total_amount}/{transaction.receipt.receipt_id}/{transaction.customer_id}"
            )
            message = transaction.model_dump_json()

            with tracer.start_as_current_span("publish_to_solace") as publish_span:
                publish_span.set_attribute("solace.topic", topic)
                POS_PUBLISHER.publish_message(topic, message, "transaction_id")
                logger.info(
                    f"Transaction {transaction.transaction_id} published to topic {topic}."
                )


async def send_aggregations(aggregation_per_store: AggregatedEvent):
    """
    Send aggregations to a separate topic for each store.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("received_aggregated_event") as received_span:
        received_span.set_attribute("event.id", str(aggregation_per_store.event_id))
        received_span.set_attribute("event.store_id", aggregation_per_store.store_id)

        topic = f"{POS_TOPIC_PREFIX}/aggregations/{aggregation_per_store.store_id}/{aggregation_per_store.event_id}/{aggregation_per_store.total_amount}"
        message = aggregation_per_store.model_dump_json()

        with tracer.start_as_current_span("publish_to_solace") as publish_span:
            publish_span.set_attribute("solace.topic", topic)
            POS_PUBLISHER.publish_message(topic, message, "event_id")
            logger.info(
                f"Aggregated event {aggregation_per_store.event_id} published to topic {topic}."
            )
