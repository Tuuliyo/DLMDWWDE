from opentelemetry import trace
from models.transaction_event import Transaction
from models.aggregated_event import AggregatedEvent
from solace_publisher import SolacePublisher
from logger_config import setup_logger
import os

# Initialize logger
logger = setup_logger()

# Configuration for the SolacePublisher to publish POS transactions
POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": f"{os.getenv('BROKER_PROTOCOL')}://{os.getenv('BROKER_HOST')}:{os.getenv('BROKER_PORT')}",
    "solace.messaging.service.vpn-name": os.getenv("BROKER_MSG_VPN"),
    "solace.messaging.authentication.scheme.basic.username": os.getenv("BROKER_SMF_USERNAME"),
    "solace.messaging.authentication.scheme.basic.password": os.getenv("BROKER_SMF_PASSWORD"),
}

# Setup topic root for POS transactions
POS_TOPIC_PREFIX = os.getenv("BROKER_POS_TOPIC_PREFIX")

# Initialize the SolacePublisher for POS transactions
POS_PUBLISHER = SolacePublisher(config=POS_TRANSACTION_CONFIG)


async def correct_transaction(transaction: Transaction):
    """
    Corrects a POS transaction and publishes it to a Solace topic.

    - Validates the total amount of the transaction and corrects it if necessary.
    - Checks the payment status and logs any issues.
    - Publishes the corrected transaction to a Solace topic.

    Args:
        transaction (Transaction): The transaction object to be corrected and published.

    OpenTelemetry Attributes:
        - `transaction.id`: The unique identifier of the transaction.
        - `transaction.store_id`: The store identifier associated with the transaction.
        - `transaction.total_amount`: The corrected total amount of the transaction.
        - `transaction.payment_status`: The payment status of the transaction.

    Logs:
        - Information about corrected totals and published transactions.
        - Warnings if the payment status is not successful.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("correct_transaction") as span:
        span.set_attribute("transaction.id", str(transaction.transaction_id))
        span.set_attribute("transaction.store_id", transaction.store_id)
        span.set_attribute("transaction.total_amount", transaction.total_amount)

        # Correct the transaction total if necessary
        calculated_total = sum(item.total_price for item in transaction.items)
        if calculated_total != transaction.total_amount:
            transaction.total_amount = round(calculated_total, 2)
            span.set_attribute("transaction.corrected_total", transaction.total_amount)
            logger.info(
                f"Corrected total for transaction {transaction.transaction_id}: {transaction.total_amount}"
            )

        # Handle payment status
        if transaction.payment_status != "success":
            span.set_attribute("transaction.payment_status", "failed")
            logger.warning(
                f"Transaction {transaction.transaction_id} failed payment validation."
            )
        else:
            span.set_attribute("transaction.payment_status", "success")
            # Construct topic and publish message
            topic = (
                f"{POS_TOPIC_PREFIX}/receipt/{transaction.store_id}/{transaction.cashier_id}/"
                f"{transaction.payment_method}/{transaction.payment_status}/{transaction.timestamp}/"
                f"{transaction.transaction_id}/{transaction.total_amount}/{transaction.receipt.receipt_id}/"
                f"{transaction.customer_id}"
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
    Publishes aggregated data for a store to a Solace topic.

    - Constructs a topic based on the store ID and aggregation details.
    - Publishes the aggregation event to the topic.

    Args:
        aggregation_per_store (AggregatedEvent): The aggregated event object to be published.

    OpenTelemetry Attributes:
        - `event.id`: The unique identifier of the aggregated event.
        - `event.store_id`: The store identifier for the aggregated data.

    Logs:
        - Information about the published aggregated event.
    """
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("received_aggregated_event") as received_span:
        received_span.set_attribute("event.id", str(aggregation_per_store.event_id))
        received_span.set_attribute("event.store_id", aggregation_per_store.store_id)

        # Construct topic and publish message
        topic = (
            f"{POS_TOPIC_PREFIX}/aggregations/{aggregation_per_store.store_id}/"
            f"{aggregation_per_store.event_id}/{aggregation_per_store.total_amount}"
        )
        message = aggregation_per_store.model_dump_json()

        with tracer.start_as_current_span("publish_to_solace") as publish_span:
            publish_span.set_attribute("solace.topic", topic)
            POS_PUBLISHER.publish_message(topic, message, "event_id")
            logger.info(
                f"Aggregated event {aggregation_per_store.event_id} published to topic {topic}."
            )
