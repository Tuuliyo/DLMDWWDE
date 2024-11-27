from opentelemetry import trace
from models import Transaction
from solace_publisher import SolacePublisher

# TODO: Implement logging and error handling for the background task.
# TODO: Implement OpenTelemetry for tracing

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


# Get the tracer for custom spans
tracer = trace.get_tracer(__name__)


async def correct_transaction(transaction: Transaction):
    """
    Simulate more complex transaction corrections with OpenTelemetry tracing.
    """
    with tracer.start_as_current_span("correct_transaction") as span:
        # Add attributes to the span
        span.set_attribute("transaction.id", str(transaction.transaction_id))
        span.set_attribute("transaction.store_id", transaction.store_id)
        span.set_attribute("transaction.total_amount", transaction.total_amount)

        # Check if the calculated total matches the total_amount
        calculated_total = sum(item.total_price for item in transaction.items)
        if calculated_total != transaction.total_amount:
            transaction.total_amount = round(calculated_total, 2)
            span.set_attribute("transaction.corrected_total", transaction.total_amount)
            print(
                f"Total amount corrected for transaction {transaction.transaction_id}: {transaction.total_amount}"
            )

        # Payment status validation
        if transaction.payment_status != "success":
            span.set_attribute("transaction.payment_status", "failed")
            print(
                f"Transaction {transaction.transaction_id} has failed payment validation!"
            )
        else:
            span.set_attribute("transaction.payment_status", "success")
            topic = (
                f"{POS_TOPIC_PREFIX}/{transaction.store_id}/{transaction.cashier_id}/{transaction.payment_method}/"
                f"{transaction.payment_status}/{transaction.timestamp}/{transaction.transaction_id}/"
                f"{transaction.total_amount}/{transaction.receipt.receipt_id}/{transaction.customer_id}"
            )
            message = transaction.model_dump_json()

            # Create a span for Solace publishing
            with tracer.start_as_current_span("publish_to_solace") as publish_span:
                publish_span.set_attribute("solace.topic", topic)
                POS_PUBLISHER.publish_message(topic, message)
                print(
                    f"Transaction {transaction.transaction_id} published to topic {topic}"
                )
