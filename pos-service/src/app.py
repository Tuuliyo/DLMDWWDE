import json
import requests
from utils import generate_transaction
import time
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Initialize OpenTelemetry tracing
def init_tracing():
    resource = Resource.create(attributes={
        "service.name": "pos-service"  # Replace with the name of your service
    })
    # Set up the tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Configure the OTLP exporter to send traces to the OpenTelemetry Collector
    otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
    span_processor = SimpleSpanProcessor(otlp_exporter)
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
            print(f"Sending transaction: {transaction_json}")

            # Start a new span for each transaction
            with tracer.start_as_current_span("send_transaction") as span:
                # Add transaction details as span attributes
                span.set_attribute("transaction.id", transaction["transaction_id"])
                span.set_attribute("transaction.store_id", transaction["store_id"])
                span.set_attribute("transaction.total_amount", transaction["total_amount"])

                try:
                    # Send the request
                    response = requests.post(
                        "http://traefik/validation-service/api/v1/pos/validate_transaction",
                        headers={"Content-Type": "application/json"},
                        data=transaction_json,
                    )

                    # Check if the request was successful
                    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                    print(f"Transaction sent successfully: {transaction['transaction_id']}")
                    span.set_status("OK")
                except requests.HTTPError as e:
                    # If a 4xx or 5xx error occurs, handle it and log the error
                    print(f"Failed to send transaction {transaction['transaction_id']}: {e}")
                    span.record_exception(e)
                    span.set_status("ERROR")
                except requests.RequestException as e:
                    # Catch other exceptions (e.g., network-related)
                    print(f"Error during request: {e}")
                    span.record_exception(e)
                    span.set_status("ERROR")

            # Increment counter
            count += 1
            if count % 1000 == 0:
                print(f"Sent {count} messages")

    except KeyboardInterrupt:
        print("Message streaming stopped.")
    finally:
        print(f"Finished sending {count} messages")


if __name__ == "__main__":
    init_tracing()
    send_1_million_messages()