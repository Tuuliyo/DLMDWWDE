from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from models import Transaction, Item, Receipt
from background_tasks import correct_transaction
from pydantic import ValidationError
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware


# Initialize OpenTelemetry tracing
def init_tracing():
    resource = Resource.create(attributes={
        "service.name": "validation-service"  # Replace with the name of your service
    })
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Configure the OTLP exporter to send traces to the OpenTelemetry Collector
    otlp_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317", insecure=True)
    span_processor = SimpleSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Automatically instrument requests
    RequestsInstrumentor().instrument()


# Initialize FastAPI application
app = FastAPI(
    title="POS Validation Service",
    description="Service to validate POS transactions",
    version="1.0",
    openapi_url="/api/v1/pos/openapi.json",
    docs_url="/api/v1/pos/docs",
    redoc_url=None,
    root_path="/validation-service",
)

# Add OpenTelemetry middleware
init_tracing()
FastAPIInstrumentor.instrument_app(app)
app.add_middleware(OpenTelemetryMiddleware)


# TODO: Add additional endpoints for the aggregated data from flink
# TODO: Add Models for aggregated data
# TODO: Add Router in FastAPI for better organization


# Custom error handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Custom error message
    error_messages = []
    for error in exc.errors():
        # Customize the error message based on the field and the error type
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


@app.post("/api/v1/pos/validate_transaction")
async def validate_transaction(
    transaction: Transaction, background_tasks: BackgroundTasks
):
    # Add the background task for more complex validation/corrections
    background_tasks.add_task(correct_transaction, transaction)

    # If basic validation passes, return a success message
    return {
        "status": "success",
        "transaction_id": transaction.transaction_id,
        "message": "transaction accepted",
    }


@app.post("/api/v1/pos/amount-per-store")
async def amount_per_store(request: Request):
    """
    Endpoint to receive aggregated data from Flink job.
    """
    body = await request.body()
    print(f"Received aggregated data: {body.decode()}")
    return {"status": "success", "message": "Aggregated data received successfully."}


@app.get("/api/v1/health", status_code=200)
async def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    return {"status": "ok", "message": "The application is healthy and running."}
