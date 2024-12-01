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

logger = setup_logger()

resource = Resource.create(attributes={"service.name": "aggregation-pipeline"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)

otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
span_processor = BatchSpanProcessor(
    otlp_exporter,
    max_queue_size=1000,
    max_export_batch_size=500,
    schedule_delay_millis=5000,
)

trace.get_tracer_provider().add_span_processor(span_processor)

tracer = trace.get_tracer(__name__)
RequestsInstrumentor().instrument()


flow = Dataflow("aggregation-pipeline")
stream = op.input("solace_input", flow, SolaceDynamicSource())
deserialized_events = op.map("deserialize", stream, deserialize_message)
valid_events = op.filter(
    "valid_events", deserialized_events, lambda event: event is not None
)
keyed_events = op.key_on("key_by_store", valid_events, lambda x: x["store_id"])
align_to_start = datetime(2024, 11, 15, 15, 40, 40, tzinfo=timezone.utc)
clock = EventClock(
    lambda e: extract_timestamp(e["timestamp"]),
    wait_for_system_duration=timedelta(seconds=1),
)
windower = TumblingWindower(length=timedelta(seconds=10), align_to=align_to_start)
aggregated_events = windowing.fold_window(
    "aggregate_by_store",
    keyed_events,
    clock=clock,
    windower=windower,
    builder=accumulator_builder,
    folder=aggregate_sales,
    merger=merger,
)

formatted_events = op.map(
    "format_in_event_structure", aggregated_events.down, format_aggregated_event
)

op.output("api_output", formatted_events, ApiDynamicSink())
