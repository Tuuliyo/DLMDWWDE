import json
import requests
import time
from utils import generate_transaction
from prometheus_client import start_http_server, Counter, Histogram
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from logger_config import setup_logger
import os

# Initialize logger
logger = setup_logger()

# Prometheus Metrics
REQUEST_COUNT = Counter("request_count", "Number of requests sent", ["status"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Latency of requests in seconds")


def init_tracing():
    """
    Initializes OpenTelemetry tracing with an OTLP exporter.

    - Sets up a tracer provider with resource attributes.
    - Configures the OTLP exporter for sending traces to a collector.
    - Instruments the `requests` library for automatic tracing.

    Raises:
        Exception: If tracing initialization fails.
    """
    resource = Resource.create(attributes={"service.name": "pos-service"})

    # Set up the tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Configure the OTLP exporter
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

    # Instrument the `requests` library
    RequestsInstrumentor().instrument()


def send_1_million_messages():
    """
    Simulates sending POS transactions to a validation service.

    - Generates POS transactions.
    - Sends each transaction to the validation service via HTTP POST.
    - Tracks performance and request metrics using Prometheus.
    - Uses OpenTelemetry for distributed tracing.

    Returns:
        None
    """
    count = 0
    tracer = trace.get_tracer(__name__)

    try:
        while count < 200000: # 1 million transactions in total (5 replicas)
            # Generate a transaction
            transaction = generate_transaction()
            transaction_json = json.dumps(transaction)
            logger.info(f"Sending transaction: {transaction_json}")

            # Create a tracing span for the transaction
            with tracer.start_as_current_span("send_transaction") as span:
                span.set_attribute("transaction.id", transaction["transaction_id"])
                span.set_attribute("transaction.store_id", transaction["store_id"])
                span.set_attribute("transaction.total_amount", transaction["total_amount"])

                start_time = time.time()
                try:
                    # Send transaction via HTTP POST
                    response = requests.post(
                        f"{os.getenv('API_PROTOCOL')}://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/validation-service/api/v1/pos/validate_transaction",
                        headers={"Content-Type": "application/json"},
                        data=transaction_json,
                        auth=(os.getenv("API_USERNAME"), os.getenv("API_PASSWORD")),
                    )
                    response.raise_for_status()
                    logger.info(
                        f"Transaction sent successfully: {transaction['transaction_id']}"
                    )
                    span.set_status("OK")
                    REQUEST_COUNT.labels(status="success").inc()
                except requests.HTTPError as e:
                    logger.error(f"HTTP error: {e}")
                    span.record_exception(e)
                    span.set_status("ERROR")
                    REQUEST_COUNT.labels(status="http_error").inc()
                except requests.RequestException as e:
                    logger.error(f"Request error: {e}")
                    span.record_exception(e)
                    span.set_status("ERROR")
                    REQUEST_COUNT.labels(status="request_error").inc()
                finally:
                    latency = time.time() - start_time
                    REQUEST_LATENCY.observe(latency)

            count += 1
            if count % 1000 == 0:
                logger.info(f"Sent {count} messages")

    except KeyboardInterrupt:
        logger.warning("Message streaming interrupted.")
    finally:
        logger.info(f"Finished sending {count} messages")


if __name__ == "__main__":
    """
    Main entry point for the POS service simulation script.

    - Starts Prometheus metrics server on port 8000.
    - Initializes tracing.
    - Sends simulated transactions to the validation service.
    """
    start_http_server(8000)
    init_tracing()
    send_1_million_messages()
