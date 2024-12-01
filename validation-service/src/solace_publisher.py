import json
from solace.messaging.messaging_service import (
    MessagingService,
    ServiceEvent,
    ReconnectionListener,
    ReconnectionAttemptListener,
    ServiceInterruptionListener,
)
from solace.messaging.resources.topic import Topic
from solace.messaging.config.retry_strategy import RetryStrategy
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.publisher.direct_message_publisher import PublishFailureListener, FailedPublishEvent
from opentelemetry import propagate, trace
from opentelemetry.trace import StatusCode, SpanKind
from solace_otel.messaging.trace.propagation import (
    OutboundMessageCarrier,
    OutboundMessageSetter,
)
from typing import Any
from logger_config import setup_logger

# Initialize logger
logger = setup_logger()

class SolacePublisher:
    def __init__(self, config: dict[str, Any]):
        self.messaging_service = self._initialize_messaging_service(config)

        # Event Handling for the messaging service
        service_handler = ServiceEventHandler()
        self.messaging_service.add_reconnection_listener(service_handler)
        self.messaging_service.add_reconnection_attempt_listener(service_handler)
        self.messaging_service.add_service_interruption_listener(service_handler)

        self.direct_publisher = self._initialize_direct_publisher()
        self.message_builder = self.messaging_service.message_builder()

    def _initialize_messaging_service(self, config: dict[str, Any]):
        """Initializes and connects the messaging service."""
        messaging_service = (
            MessagingService.builder()
            .from_properties(config)
            .with_reconnection_retry_strategy(RetryStrategy.parametrized_retry(20, 3))
            .build()
        )
        messaging_service.connect()
        logger.info(f"Messaging Service connected? {messaging_service.is_connected}")
        return messaging_service

    def _initialize_direct_publisher(self):
        """Initializes the direct message publisher."""
        direct_publisher = (
            self.messaging_service.create_direct_message_publisher_builder()
            .build()
        )
        direct_publisher.set_publish_failure_listener(PublisherErrorHandling())
        direct_publisher.start()
        logger.info(f"Direct Publisher ready? {direct_publisher.is_ready()}")
        return direct_publisher

    def publish_message(self, topic: str, message: str, application_message_id: str):
        """Publishes messages to a topic with transaction_id as the message ID."""
        try:
            topic_obj = Topic.of(topic)

            # Parse the message body to extract transaction_id
            try:
                message_content = json.loads(message)
                application_message_id = message_content[application_message_id]
                if not application_message_id:
                    raise ValueError("Missing application_message_id in message content")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing message body: {e}")
                return

            outbound_msg = (
                self.message_builder
                .with_application_message_id(application_message_id)
                .with_property("application", "json")
                .build(message)
            )

            tracer = trace.get_tracer("SolacePublisherTracer")
            propagator = propagate.get_global_textmap()
            with tracer.start_as_current_span(f"{topic}_publish", kind=SpanKind.PRODUCER) as span:
                # Set attributes for the span
                span.set_attribute("messaging.system", "PubSub+")
                span.set_attribute("messaging.destination_kind", "topic")
                span.set_attribute("messaging.destination", topic)
                span.set_attribute("messaging.protocol", "SMF")
                span.set_attribute("messaging.operation", "publish")

                # Create an OutboundMessageCarrier and inject context into it
                carrier = OutboundMessageCarrier(outbound_msg)
                default_setter = OutboundMessageSetter()
                propagator.inject(carrier=carrier, setter=default_setter)

                try:
                    # Publish the message
                    self.direct_publisher.publish(destination=topic_obj, message=outbound_msg)
                    span.set_status(StatusCode.OK)
                    logger.info(f"Message published to topic: {topic}")
                except Exception as e:
                    logger.error(f"Error publishing message: {e}")
                    span.set_status(StatusCode.ERROR, str(e))

        except KeyboardInterrupt:
            logger.warning("Publishing interrupted by user.")
        except PubSubPlusClientError as e:
            logger.error(f"Error publishing message: {e}")

    def close(self):
        """Gracefully shuts down the publisher and messaging service."""
        if self.direct_publisher and self.direct_publisher.is_ready():
            self.direct_publisher.terminate()
            logger.info("Direct publisher terminated.")
        if self.messaging_service and self.messaging_service.is_connected:
            self.messaging_service.disconnect()
            logger.info("Messaging service disconnected.")


class ServiceEventHandler(
    ReconnectionListener, ReconnectionAttemptListener, ServiceInterruptionListener
):
    def on_reconnected(self, e: ServiceEvent):
        logger.info("Reconnected to the messaging service.")
        logger.debug(f"Error cause: {e.get_cause()}")
        logger.debug(f"Message: {e.get_message()}")

    def on_reconnecting(self, e: "ServiceEvent"):
        logger.warning("Attempting to reconnect to the messaging service.")
        logger.debug(f"Error cause: {e.get_cause()}")
        logger.debug(f"Message: {e.get_message()}")

    def on_service_interrupted(self, e: "ServiceEvent"):
        logger.error("Messaging service interrupted.")
        logger.debug(f"Error cause: {e.get_cause()}")
        logger.debug(f"Message: {e.get_message()}")


class PublisherErrorHandling(PublishFailureListener):
    def on_failed_publish(self, e: "FailedPublishEvent"):
        logger.error("Failed to publish message.")
        logger.debug(f"Failed Publish Event: {e}")
