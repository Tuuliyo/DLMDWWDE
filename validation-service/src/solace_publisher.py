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
from solace.messaging.config.authentication_strategy import BasicUserNamePassword
from solace.messaging.errors.pubsubplus_client_error import PubSubPlusClientError
from solace.messaging.publisher.direct_message_publisher import PublishFailureListener, FailedPublishEvent
from typing import Any


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
        print(f"Messaging Service connected? {messaging_service.is_connected}")
        return messaging_service

    def _initialize_direct_publisher(self):
        """Initializes the direct message publisher."""
        direct_publisher = (
            self.messaging_service.create_direct_message_publisher_builder()
            .build()
        )
        direct_publisher.set_publish_failure_listener(PublisherErrorHandling())
        direct_publisher.start()
        print(f"Direct Publisher ready? {direct_publisher.is_ready()}")
        return direct_publisher

    def publish_message(self, topic: str, message: str):
        """Publishes messages to a topic with transaction_id as the message ID."""
        try:
            topic_obj = Topic.of(topic)

            # Parse the message body to extract transaction_id
            try:
                message_content = json.loads(message)
                transaction_id = message_content["transaction_id"]
                if not transaction_id:
                    raise ValueError("Missing transaction_id in message content")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error processing message body: {e}")

            # Create the message with transaction_id as the message ID
            outbound_msg = (
                self.message_builder
                .with_application_message_id(transaction_id)  # Use transaction_id as message ID
                .with_property("application", "json")
                .build(message)  # Add count to the payload for tracking
            )

            # Publish the message
            self.direct_publisher.publish(destination=topic_obj, message=outbound_msg)
            #print(f"Message published to topic {topic_obj}")


        except KeyboardInterrupt:
            print("Publishing interrupted by user.")
        except PubSubPlusClientError as e:
            print(f"Error publishing message: {e}")

    def close(self):
        """Gracefully shuts down the publisher and messaging service."""
        if self.direct_publisher and self.direct_publisher.is_ready():
            self.direct_publisher.terminate()
            print("Direct publisher terminated.")
        if self.messaging_service and self.messaging_service.is_connected:
            self.messaging_service.disconnect()
            print("Messaging service disconnected.")


class ServiceEventHandler(
    ReconnectionListener, ReconnectionAttemptListener, ServiceInterruptionListener
):
    def on_reconnected(self, e: ServiceEvent):
        print("\non_reconnected")
        print(f"Error cause: {e.get_cause()}")
        print(f"Message: {e.get_message()}")

    def on_reconnecting(self, e: "ServiceEvent"):
        print("\non_reconnecting")
        print(f"Error cause: {e.get_cause()}")
        print(f"Message: {e.get_message()}")

    def on_service_interrupted(self, e: "ServiceEvent"):
        print("\non_service_interrupted")
        print(f"Error cause: {e.get_cause()}")
        print(f"Message: {e.get_message()}")


class PublisherErrorHandling(PublishFailureListener):
    def on_failed_publish(self, e: "FailedPublishEvent"):
        print("on_failed_publish")
