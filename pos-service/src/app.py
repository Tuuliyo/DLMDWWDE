import json
import requests
import time
from utils import generate_transaction
from prometheus_client import start_http_server, Counter, Histogram
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from logger_config import setup_logger

logger = setup_logger()

# Prometheus metrics
REQUEST_COUNT = Counter("request_count", "Number of requests sent", ["status"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "Latency of requests in seconds")

# Initialize OpenTelemetry tracing
def init_tracing():
    resource = Resource.create(attributes={
        "service.name": "pos-service"  # Replace with the name of your service
    })
    # Set up the tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Configure the OTLP exporter to send traces to the OpenTelemetry Collector
    otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter, max_queue_size=1000, max_export_batch_size=500, schedule_delay_millis=5000)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Automatically instrument requests library
    RequestsInstrumentor().instrument()

# Main function to send 1,000,000 messages
def send_1_million_messages():
    count = 0
    tracer = trace.get_tracer(__name__)  # Get the tracer for this module

    try:
        while count < 50000:
            # Generate a random POS transaction
            transaction = generate_transaction()

            # Convert transaction to JSON format
            transaction_json = json.dumps(transaction)
            logger.info(f"Sending transaction: {transaction_json}")

            # Start a new span for each transaction
            with tracer.start_as_current_span("send_transaction") as span:
                # Add transaction details as span attributes
                span.set_attribute("transaction.id", transaction["transaction_id"])
                span.set_attribute("transaction.store_id", transaction["store_id"])
                span.set_attribute("transaction.total_amount", transaction["total_amount"])

                start_time = time.time()  # Start latency timer
                try:
                    # Send the request
                    response = requests.post(
                        "http://traefik/validation-service/api/v1/pos/validate_transaction",
                        headers={"Content-Type": "application/json"},
                        data=transaction_json,
                    )

                    # Check if the request was successful
                    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                    logger.info(f"Transaction sent successfully: {transaction['transaction_id']}")
                    span.set_status("OK")

                    # Increment Prometheus counter for successful requests
                    REQUEST_COUNT.labels(status="success").inc()
                except requests.HTTPError as e:
                    # If a 4xx or 5xx error occurs, handle it and log the error
                    logger.error(f"Failed to send transaction {transaction['transaction_id']}: {e}")
                    span.record_exception(e)
                    span.set_status("ERROR")

                    # Increment Prometheus counter for failed requests
                    REQUEST_COUNT.labels(status="http_error").inc()
                except requests.RequestException as e:
                    # Catch other exceptions (e.g., network-related)
                    logger.error(f"Error during request: {e}")
                    span.record_exception(e)
                    span.set_status("ERROR")

                    # Increment Prometheus counter for failed requests
                    REQUEST_COUNT.labels(status="request_error").inc()
                finally:
                    latency = time.time() - start_time  # Calculate latency
                    REQUEST_LATENCY.observe(latency)  # Record latency in Prometheus

            # Increment counter
            count += 1
            if count % 1000 == 0:
                logger.info(f"Sent {count} messages")

    except KeyboardInterrupt:
        logger.warning("Message streaming stopped.")
    finally:
        logger.info(f"Finished sending {count} messages")


if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(8000)

    # Initialize tracing and start sending messages
    init_tracing()
    send_1_million_messages()
