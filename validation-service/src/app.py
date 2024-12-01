from fastapi import FastAPI, BackgroundTasks, Request
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
from models.transaction_event import Transaction
from models.aggregated_event import AggregatedEvent
from routes import transaction
from prometheus_fastapi_instrumentator import Instrumentator


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
instrumentor = Instrumentator().instrument(app)
app.add_middleware(OpenTelemetryMiddleware)

app.include_router(transaction.router)

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


# @app.post("/api/v1/pos/validate_transaction")
# async def validate_transaction(
#     transaction: Transaction, background_tasks: BackgroundTasks
# ):
#     tracer = trace.get_tracer(__name__)  # Get tracer for custom spans

#     with tracer.start_as_current_span("validate_transaction") as span:
#         span.set_attribute("transaction.id", str(transaction.transaction_id))
#         span.set_attribute("transaction.store_id", transaction.store_id)

#         try:
#             # Add the background task for more complex validation/corrections
#             background_tasks.add_task(correct_transaction, transaction)
#             return {
#                 "status": "success",
#                 "transaction_id": transaction.transaction_id,
#                 "message": "transaction accepted",
#             }
#         except Exception as e:
#             span.record_exception(e)
#             span.set_status("ERROR")
#             raise e


@app.post("/api/v1/pos/amount-per-store")
async def amount_per_store(
    aggregated_event: AggregatedEvent, background_tasks: BackgroundTasks
):
    """
    Endpoint to receive aggregated data from Flink job.
    """
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("amount_per_store") as span:
        span.set_attribute("event.id", str(aggregated_event.event_id))
        span.set_attribute("event.store_id", aggregated_event.store_id)

        try:
            print(f"Received aggregated data: {aggregated_event}")
            background_tasks.add_task(send_aggregations, aggregated_event)
            return {
                "status": "success",
                "message": "Aggregated data received successfully.",
            }
        except Exception as e:
            span.record_exception(e)
            span.set_status("ERROR")
            raise e


@app.get("/api/v1/health", status_code=200)
async def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    return {"status": "ok", "message": "The application is healthy and running."}
