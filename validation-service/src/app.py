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

# Initialize logger
logger = setup_logger()

# Initialize OpenTelemetry tracing
def init_tracing():
    resource = Resource.create(
        attributes={
            "service.name": "validation-service"  # Set the service name for tracing
        }
    )
    trace.set_tracer_provider(TracerProvider(resource=resource))

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

    # Automatically instrument requests
    RequestsInstrumentor().instrument()


# Initialize FastAPI application
app = FastAPI(
    title="Validation Service",
    description="Service to validate events send to message broker",
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

app.include_router(transaction.router)
app.include_router(health.router)
app.include_router(amount_per_store.router)

@app.on_event("startup")
async def startup_event():
    print("Validation Service started")
    instrumentor.expose(app)

# Custom error handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for error in exc.errors():
        field = error.get("loc")[-1]  # Get the field name
        msg = error.get("msg")  # Get the error message
        error_messages.append(f"Field '{field}' validation failed: {msg}")

    print(f"Validation error: {error_messages}")
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
