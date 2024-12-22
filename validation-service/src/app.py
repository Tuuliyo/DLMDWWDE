from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from routes import transaction, health, amount_per_store
from prometheus_fastapi_instrumentator import Instrumentator
from logger_config import setup_logger
import os

# Initialize logger
logger = setup_logger()

def init_tracing():
    """
    Initializes OpenTelemetry tracing for the application.

    - Configures the tracer provider with resource attributes.
    - Sets up the OTLP exporter to send traces to the OpenTelemetry Collector.
    - Adds a batch span processor for optimized trace export.
    - Instruments the `requests` library for tracing HTTP requests.

    Raises:
        Exception: If tracing initialization fails.
    """
    resource = Resource.create(
        attributes={"service.name": "validation-service"}
    )
    trace.set_tracer_provider(TracerProvider(resource=resource))

    otlp_exporter = OTLPSpanExporter(
        endpoint=f"{os.getenv('OTEL_COLLECTOR_PROTOCOL')}://{os.getenv('OTEL_COLLECTOR_HOST')}:{os.getenv('OTEL_COLLECTOR_PORT')}", insecure=True
    )
    span_processor = BatchSpanProcessor(
        otlp_exporter,
        max_queue_size=1000,
        max_export_batch_size=500,
        schedule_delay_millis=5000,
    )
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Automatically instrument requests
    RequestsInstrumentor().instrument()


# Initialize FastAPI application
app = FastAPI(
    title="Validation Service",
    description="Service to validate events sent to the message broker",
    version="1.0",
    openapi_url="/api/v1/pos/openapi.json",
    docs_url="/api/v1/pos/docs",
    redoc_url=None,
    root_path="/validation-service",
)

# Add OpenTelemetry middleware
init_tracing()
FastAPIInstrumentor.instrument_app(app)
instrumentor = Instrumentator().instrument(app)
app.add_middleware(OpenTelemetryMiddleware)

# Include routers for different endpoints
app.include_router(transaction.router)
app.include_router(health.router)
app.include_router(amount_per_store.router)

@app.on_event("startup")
async def startup_event():
    """
    Event triggered when the application starts.

    - Logs the startup event.
    - Exposes Prometheus metrics via the application.
    """
    logger.info("Validation Service started")
    instrumentor.expose(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom exception handler for FastAPI request validation errors.

    - Extracts detailed validation error messages.
    - Logs validation errors.
    - Returns a JSON response with status 422 and error details.

    Args:
        request (Request): The incoming request object.
        exc (RequestValidationError): The validation error raised by FastAPI.

    Returns:
        JSONResponse: A structured error response with validation details.
    """
    error_messages = []
    for error in exc.errors():
        field = error.get("loc")[-1]  # Get the field name
        msg = error.get("msg")  # Get the error message
        error_messages.append(f"Field '{field}' validation failed: {msg}")

    logger.error(f"Validation error: {error_messages}")
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {
                "status": "error",
                "message": "Validation failed for the request body",
                "errors": error_messages,
            }
        ),
    )
