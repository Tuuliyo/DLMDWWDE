import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from bytewax.inputs import DynamicSource, StatelessSourcePartition
from bytewax.operators.windowing import EventClock, TumblingWindower
import bytewax.operators.windowing as windowing
import json
import uuid
from datetime import datetime, timedelta, timezone
import requests
import logging
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
from opentelemetry import propagate, context, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import StatusCode, SpanKind
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Solace configuration
POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": "tcp://message-broker:55555",
    "solace.messaging.service.vpn-name": "default",
    "solace.messaging.authentication.scheme.basic.username": "testuser",
    "solace.messaging.authentication.scheme.basic.password": "Test1234!",
}
POS_QUEUE_NAME = "sale.pos.transaction.aggregation.service"

# Initialize OpenTelemetry tracing
resource = Resource.create(attributes={"service.name": "aggregation-pipeline"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure the OTLP exporter to send traces to the OpenTelemetry Collector
otlp_exporter = OTLPSpanExporter(
    endpoint="http://otel-collector:4317", insecure=True
)
span_processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=1000,
    max_export_batch_size=500,
    schedule_delay_millis=5000,
)
trace.get_tracer_provider().add_span_processor(span_processor)


tracer = trace.get_tracer(__name__)
RequestsInstrumentor().instrument()

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
        logging.info(f"Messaging Service connected: {messaging_service.is_connected}")
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
            logging.info(
                f"Receiver started. Bound to Queue [{durable_exclusive_queue.get_name()}]"
            )
            return persistent_receiver
        except PubSubPlusClientError as e:
            logging.error(f"Failed to initialize receiver: {e}")
            raise

    def next_batch(self):
        try:
            message = self.receiver.receive_message(
                timeout=1
            )  # Set an appropriate timeout
            if message:
                # Extract context from incoming message
                PROPAGATOR = propagate.get_global_textmap()
                carrier = InboundMessageCarrier(message)
                extracted_ctx = PROPAGATOR.extract(
                    carrier=carrier, getter=InboundMessageGetter()
                )

                # Attach the extracted context
                token = context.attach(extracted_ctx)
                try:
                    # Create a new span for message processing
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
                        logging.info(f"Received message: {payload}")
                        self.receiver.ack(message)
                        span.set_status(StatusCode.OK)
                        return [payload]
                except Exception as e:
                    logging.error(f"Error processing message: {e}")
                    span.set_status(StatusCode.ERROR)
                    span.record_exception(e)
            else:
                return []
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            return []

    def next_awake(self):
        return None

    def close(self):
        """Gracefully shuts down the consumer."""
        if self.receiver:
            self.receiver.terminate()
            logging.info("Receiver terminated.")
        if self.messaging_service.is_connected:
            self.messaging_service.disconnect()
            logging.info("Messaging service disconnected.")


class SolaceDynamicSource(DynamicSource):
    def build(self, step_id, worker_index, worker_count):
        return SolaceSourcePartition()


class ApiSinkPartition(StatelessSinkPartition):
    def write_batch(self, items):
        for item in items:
            logging.info(f"Sending to API: {item}")
            try:
                with tracer.start_as_current_span(
                    "send_event_to_api", kind=SpanKind.CLIENT
                ) as send_span:
                    send_span.set_attribute("http.method", "POST")
                    send_span.set_attribute(
                        "http.url",
                        "http://traefik/validation-service/api/v1/pos/amount-per-store",
                    )
                    send_span.set_attribute("event.id", item["event_id"])
                    send_span.set_attribute("store.id", item["store_id"])

                    send_to_api(item)

            except Exception as e:
                logging.error(f"Failed to send item {item}: {e}")
                send_span.set_status(StatusCode.ERROR)
                send_span.record_exception(e)

    def close(self):
        logging.info("Closing ApiSinkPartition")


class ApiDynamicSink(DynamicSink):
    def build(self, step_id, worker_index, worker_count):
        return ApiSinkPartition()


def send_to_api(aggregated_data):
    url = "http://traefik/validation-service/api/v1/pos/amount-per-store"
    try:
        response = requests.post(url, json=aggregated_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send data: {e}")


# Deserialize JSON events into a Python dictionary
def deserialize_message(event: str):
    try:
        return json.loads(event)
    except json.JSONDecodeError:
        logging.error("Error decoding JSON")
        return None


# Define Timestamp Extraction Function
def extract_timestamp(timestamp_str):
    return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))


# Accumulator Functions
def accumulator_builder():
    return {"total_amount": 0.0, "min_timestamp": None, "max_timestamp": None}


def aggregate_sales(accumulator, event):
    amount = event["total_amount"]
    event_time = extract_timestamp(event["timestamp"])

    accumulator["total_amount"] += amount

    # Update min_timestamp
    if (
        accumulator["min_timestamp"] is None
        or event_time < accumulator["min_timestamp"]
    ):
        accumulator["min_timestamp"] = event_time

    # Update max_timestamp
    if (
        accumulator["max_timestamp"] is None
        or event_time > accumulator["max_timestamp"]
    ):
        accumulator["max_timestamp"] = event_time

    return accumulator


def merger(acc1, acc2):
    return {
        "total_amount": acc1["total_amount"] + acc2["total_amount"],
        "min_timestamp": min(
            acc1["min_timestamp"] or acc2["min_timestamp"],
            acc2["min_timestamp"] or acc1["min_timestamp"],
        ),
        "max_timestamp": max(
            acc1["max_timestamp"] or acc2["max_timestamp"],
            acc2["max_timestamp"] or acc1["max_timestamp"],
        ),
    }


# Build the dataflow
flow = Dataflow("aggregation-pipeline")

# Input Stream
stream = op.input("solace_input", flow, SolaceDynamicSource())

# Deserialize Events
deserialized_events = op.map("deserialize", stream, deserialize_message)

# Filter None Events
valid_events = op.filter(
    "valid_events", deserialized_events, lambda event: event is not None
)

# Key Events by Store ID
keyed_events = op.key_on("key_by_store", valid_events, lambda x: x["store_id"])

# Clock and Window Configuration
align_to_start = datetime(2024, 11, 15, 15, 40, 40, tzinfo=timezone.utc)
clock = EventClock(
    lambda e: extract_timestamp(e["timestamp"]),
    wait_for_system_duration=timedelta(seconds=1),
)
windower = TumblingWindower(length=timedelta(seconds=10), align_to=align_to_start)

# Aggregation with fold_window
aggregated_events = windowing.fold_window(
    "aggregate_by_store",
    keyed_events,
    clock=clock,
    windower=windower,
    builder=accumulator_builder,
    folder=aggregate_sales,
    merger=merger,
)


# Transform the aggregated events to the desired format
def format_aggregated_event(item):
    key, (window, accumulator) = item
    accumulator["event_id"] = str(uuid.uuid4())
    accumulator["store_id"] = key
    accumulator["total_amount"] = round(accumulator["total_amount"], 2)
    accumulator["begin_stream_aggregator"] = (
        accumulator["min_timestamp"].isoformat()
        if accumulator["min_timestamp"]
        else None
    )
    accumulator["end_stream_aggregator"] = (
        accumulator["max_timestamp"].isoformat()
        if accumulator["max_timestamp"]
        else None
    )
    # Remove intermediate fields
    del accumulator["min_timestamp"]
    del accumulator["max_timestamp"]
    return accumulator


formatted_events = op.map(
    "format_in_event_structure", aggregated_events.down, format_aggregated_event
)

# Output
op.output("api_output", formatted_events, ApiDynamicSink())
