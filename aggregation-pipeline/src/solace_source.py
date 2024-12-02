from solace.messaging.messaging_service import MessagingService
from solace.messaging.resources.queue import Queue
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.receiver.persistent_message_receiver import (
    PersistentMessageReceiver,
)
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.config.missing_resources_creation_configuration import (
    MissingResourcesCreationStrategy,
)
from solace_otel.messaging.trace.propagation import (
    InboundMessageCarrier,
    InboundMessageGetter,
)
from bytewax.inputs import DynamicSource, StatelessSourcePartition
from opentelemetry import propagate, context, trace
from opentelemetry.trace import StatusCode, SpanKind
from logger_config import setup_logger

logger = setup_logger()
tracer = trace.get_tracer(__name__)


POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": "tcp://message-broker:55555",
    "solace.messaging.service.vpn-name": "default",
    "solace.messaging.authentication.scheme.basic.username": "sale_pos_transaction_aggregation",
    "solace.messaging.authentication.scheme.basic.password": "Aggregation1234!",
}
POS_QUEUE_NAME = "sale_pos_transaction_aggregation_service"


class SolaceSourcePartition(StatelessSourcePartition):
    def __init__(self):
        self.messaging_service = self._initialize_messaging_service(
            POS_TRANSACTION_CONFIG
        )
        self.receiver = self._initialize_persistent_receiver(POS_QUEUE_NAME)

    def _initialize_messaging_service(self, config):
        """Initializes and connects the messaging service."""
        messaging_service = (
            MessagingService.builder()
            .from_properties(config)
            .with_reconnection_retry_strategy(
                RetryStrategy.parametrized_retry(20, 5000)
            )
            .build()
        )
        messaging_service.connect()
        logger.info(f"Messaging Service connected: {messaging_service.is_connected}")
        return messaging_service

    def _initialize_persistent_receiver(self, queue_name):
        """Initializes the persistent message receiver."""
        durable_exclusive_queue = Queue.durable_exclusive_queue(queue_name)
        try:
            persistent_receiver: PersistentMessageReceiver = (
                self.messaging_service.create_persistent_message_receiver_builder()
                .with_missing_resources_creation_strategy(
                    MissingResourcesCreationStrategy.CREATE_ON_START
                )
                .build(durable_exclusive_queue)
            )
            persistent_receiver.start()
            logger.info(
                f"Receiver started. Bound to Queue [{durable_exclusive_queue.get_name()}]"
            )
            return persistent_receiver
        except PubSubPlusClientError as e:
            logger.error(f"Failed to initialize receiver: {e}")
            raise

    def next_batch(self):
        try:
            message = self.receiver.receive_message(timeout=1)
            if message:
                PROPAGATOR = propagate.get_global_textmap()
                carrier = InboundMessageCarrier(message)
                extracted_ctx = PROPAGATOR.extract(
                    carrier=carrier, getter=InboundMessageGetter()
                )

                token = context.attach(extracted_ctx)
                try:
                    with tracer.start_as_current_span(
                        "process_message", kind=SpanKind.CONSUMER
                    ) as span:
                        span.set_attribute("messaging.system", "PubSub+")
                        span.set_attribute("messaging.destination_kind", "queue")
                        span.set_attribute(
                            "messaging.destination", message.get_destination_name()
                        )
                        span.set_attribute("messaging.operation", "process")

                        payload = (
                            message.get_payload_as_string()
                            or message.get_payload_as_bytes().decode()
                        )
                        logger.info(f"Received message: {payload}")
                        self.receiver.ack(message)
                        span.set_status(StatusCode.OK)
                        return [payload]
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    span.set_status(StatusCode.ERROR)
                    span.record_exception(e)
            else:
                return []
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return []

    def close(self):
        """Gracefully shuts down the consumer."""
        if self.receiver:
            self.receiver.terminate()
            logger.info("Receiver terminated.")
        if self.messaging_service.is_connected:
            self.messaging_service.disconnect()
            logger.info("Messaging service disconnected.")


class SolaceDynamicSource(DynamicSource):
    def build(self, step_id, worker_index, worker_count):
        return SolaceSourcePartition()
