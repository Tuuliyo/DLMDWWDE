import queue
import logging
from solace.messaging.messaging_service import (
    MessagingService,
    ReconnectionListener,
    ReconnectionAttemptListener,
    ServiceInterruptionListener,
    ServiceEvent,
)
from solace.messaging.resources.queue import Queue
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.receiver.persistent_message_receiver import (
    PersistentMessageReceiver,
)
from solace.messaging.receiver.message_receiver import MessageHandler, InboundMessage
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.config.missing_resources_creation_configuration import (
    MissingResourcesCreationStrategy,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Thread-safe queue for buffering Solace messages
message_queue = queue.Queue(maxsize=100000)


class SolaceConsumer:
    def __init__(self, config: dict, queue_name: str):
        self.messaging_service = self._initialize_messaging_service(config)
        self.receiver = self._initialize_persistent_receiver(queue_name)

    def _initialize_messaging_service(self, config: dict):
        """Initializes and connects the messaging service."""
        messaging_service = (
            MessagingService.builder()
            .from_properties(config)
            .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20, 3000))
            .build()
        )
        messaging_service.connect()
        logging.info(f"Messaging Service connected: {messaging_service.is_connected}")
        return messaging_service

    def _initialize_persistent_receiver(self, queue_name: str):
        """Initializes the persistent message receiver."""
        durable_exclusive_queue = Queue.durable_exclusive_queue(queue_name)
        try:
            persistent_receiver: PersistentMessageReceiver = (
                self.messaging_service.create_persistent_message_receiver_builder()
                .with_missing_resources_creation_strategy(MissingResourcesCreationStrategy.CREATE_ON_START)
                .build(durable_exclusive_queue)
            )
            persistent_receiver.start()
            persistent_receiver.receive_async(MessageHandlerImpl(persistent_receiver))
            logging.info(f"Receiver started. Bound to Queue [{durable_exclusive_queue.get_name()}]")
            return persistent_receiver
        except PubSubPlusClientError as e:
            logging.error(f"Failed to initialize receiver: {e}")
            raise

    def shutdown(self):
        """Gracefully shuts down the consumer."""
        if self.receiver:
            self.receiver.terminate()
            logging.info("Receiver terminated.")
        if self.messaging_service.is_connected:
            self.messaging_service.disconnect()
            logging.info("Messaging service disconnected.")


class MessageHandlerImpl(MessageHandler):
    def __init__(self, persistent_receiver: PersistentMessageReceiver):
        self.receiver = persistent_receiver

    def on_message(self, message: InboundMessage):
        payload = message.get_payload_as_string() or message.get_payload_as_bytes().decode()
        #logging.info(f"Received message: {payload}")
        topic = message.get_destination_name()
        #logging.info("\n" + f"Received message on: {topic}")
        try:
            message_queue.put(payload, timeout=0.0001)  # Add message to queue
            self.receiver.ack(message)  # Acknowledge message
        except queue.Full:
            logging.warning("Message queue is full. Dropping message.")
