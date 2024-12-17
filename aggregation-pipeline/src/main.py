import bytewax.operators as op
from bytewax.dataflow import Dataflow
from bytewax.operators.windowing import EventClock, TumblingWindower
import bytewax.operators.windowing as windowing
from datetime import datetime, timedelta, timezone
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from logger_config import setup_logger
from utils import (
    deserialize_message,
    extract_timestamp,
    accumulator_builder,
    aggregate_sales,
    merger,
    format_aggregated_event,
)
from solace_source import SolaceDynamicSource
from api_sink import ApiDynamicSink
from prometheus_client import start_http_server

# Initialize logger
logger = setup_logger()

# Configure OpenTelemetry for tracing
resource = Resource.create(attributes={"service.name": "aggregation-pipeline"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

# Configure OTLP exporter for sending spans to the OpenTelemetry Collector
otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=1000,
    max_export_batch_size=500,
    schedule_delay_millis=5000,
)
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)

# Instrument HTTP requests for tracing
RequestsInstrumentor().instrument()
start_http_server(8000)

# Define the dataflow
flow = Dataflow("aggregation-pipeline")

# Input: Source data from Solace
stream = op.input("solace_input", flow, SolaceDynamicSource())

# Step 1: Deserialize incoming messages
deserialized_events = op.map("deserialize", stream, deserialize_message)

# Step 2: Filter valid events
valid_events = op.filter(
    "valid_events", deserialized_events, lambda event: event is not None
)

# Step 3: Key events by store ID for aggregation
keyed_events = op.key_on("key_by_store", valid_events, lambda x: x["store_id"])

# Step 4: Define windowing parameters for event aggregation
align_to_start = datetime(2024, 11, 15, 0, 0, 0, tzinfo=timezone.utc)  # Window alignment
clock = EventClock(
    lambda e: extract_timestamp(e["timestamp"]),  # Extract timestamp from events
    wait_for_system_duration=timedelta(seconds=0.1),  # Minimal delay for late events
)
windower = TumblingWindower(length=timedelta(seconds=10), align_to=align_to_start)

# Step 5: Aggregate events in the defined window
aggregated_events = windowing.fold_window(
    "aggregate_by_store",
    keyed_events,
    clock=clock,
    windower=windower,
    builder=accumulator_builder,  # Create the accumulator
    folder=aggregate_sales,  # Aggregate sales data
    merger=merger,  # Merge accumulators across partitions
)

# Step 6: Format the aggregated events into the desired structure
formatted_events = op.map(
    "format_in_event_structure", aggregated_events.down, format_aggregated_event
)

# Output: Send formatted events to the API
op.output("api_output", formatted_events, ApiDynamicSink())
