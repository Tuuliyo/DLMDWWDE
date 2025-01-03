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
import os

# Initialize logger and tracer
logger = setup_logger()
tracer = trace.get_tracer(__name__)

# Configuration for Solace Messaging Service
POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": f"{os.getenv('BROKER_SMF_PROTOCOL')}://{os.getenv('BROKER_SMF_HOST')}:{os.getenv('BROKER_SMF_PORT')}",
    "solace.messaging.service.vpn-name": os.getenv("BROKER_MSG_VPN", "default"),
    "solace.messaging.authentication.scheme.basic.username": os.getenv("BROKER_SMF_USERNAME"),
    "solace.messaging.authentication.scheme.basic.password": os.getenv("BROKER_SMF_PASSWORD"),
}
POS_QUEUE_NAME = os.getenv('BROKER_QUEUE_NAME')


class SolaceSourcePartition(StatelessSourcePartition):
    """
    A source partition for consuming messages from a Solace queue.

    Handles message receiving, processing, acknowledgment, and tracing integration.
    """

    def __init__(self):
        """
        Initializes the source partition by setting up the messaging service and receiver.
        """
        self.messaging_service = self._initialize_messaging_service(
            POS_TRANSACTION_CONFIG
        )
        self.receiver = self._initialize_persistent_receiver(POS_QUEUE_NAME)

    def _initialize_messaging_service(self, config):
        """
        Initializes and connects the Solace Messaging Service.

        Args:
            config (dict): Configuration dictionary for Solace Messaging Service.

        Returns:
            MessagingService: Connected messaging service instance.
        """
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
        """
        Initializes the persistent message receiver for a given queue.

        Args:
            queue_name (str): Name of the Solace queue.

        Returns:
            PersistentMessageReceiver: Initialized and started message receiver.
        """
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
        """
        Receives the next batch of messages from the queue.

        Processes messages with tracing and acknowledges them upon successful processing.

        Returns:
            list[str]: A list of payloads from the processed messages.
        """
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

                        # Extract message payload
                        payload = (
                            message.get_payload_as_string()
                            or message.get_payload_as_bytes().decode()
                        )
                        logger.info(f"Received message: {payload}")

                        # Acknowledge the message
                        self.receiver.ack(message)

                        # Set trace status to OK
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
        """
        Gracefully shuts down the source partition by terminating the receiver
        and disconnecting the messaging service.
        """
        if self.receiver:
            self.receiver.terminate()
            logger.info("Receiver terminated.")
        if self.messaging_service.is_connected:
            self.messaging_service.disconnect()
            logger.info("Messaging service disconnected.")


class SolaceDynamicSource(DynamicSource):
    """
    A dynamic source for consuming messages from Solace.

    Builds source partitions for distributed processing.
    """

    def build(self, step_id, worker_index, worker_count):
        """
        Builds and returns a new source partition.

        Args:
            step_id (str): The ID of the pipeline step.
            worker_index (int): The index of the current worker.
            worker_count (int): The total number of workers.

        Returns:
            SolaceSourcePartition: A new instance of the source partition.
        """
        return SolaceSourcePartition()
