from fastapi import APIRouter, BackgroundTasks, Depends
from models.aggregated_event import AggregatedEvent
from opentelemetry import trace
from background_tasks import send_aggregations
from logger_config import setup_logger
from utils import validate_basic_auth

# Initialize logger
logger = setup_logger()

# Initialize API router
router = APIRouter()


@router.post("/api/v1/pos/amount-per-store", status_code=200, tags=["Aggregations"])
async def amount_per_store(
    aggregated_event: AggregatedEvent,
    background_tasks: BackgroundTasks,
    username: str = Depends(validate_basic_auth),
):
    """
    Endpoint to process aggregated data from a Flink job.

    This endpoint:
    - Validates the incoming aggregated event data.
    - Logs the received data and the authenticated username.
    - Adds a background task to send the aggregations for further processing.
    - Traces the operation using OpenTelemetry for observability.

    Args:
        aggregated_event (AggregatedEvent): The aggregated data object received from the Flink job.
        background_tasks (BackgroundTasks): FastAPI's background task manager for running tasks asynchronously.
        username (str): Authenticated username extracted via Basic Auth.

    Returns:
        dict: A response dictionary with a success message.

    Raises:
        Exception: If an error occurs during processing, the exception is logged and re-raised.

    OpenTelemetry Attributes:
        - `event.id`: The unique identifier for the aggregated event.
        - `event.store_id`: The store identifier associated with the aggregated event.
    """
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("amount_per_store") as span:
        # Set OpenTelemetry span attributes
        span.set_attribute("event.id", str(aggregated_event.event_id))
        span.set_attribute("event.store_id", aggregated_event.store_id)

        try:
            # Log received data and username
            logger.info(
                f"User '{username}' received aggregated data: {aggregated_event}"
            )

            # Add the background task for further processing
            background_tasks.add_task(send_aggregations, aggregated_event)

            # Return success response
            return {
                "status": "success",
                "message": "Aggregated data received successfully.",
            }
        except Exception as e:
            # Log and trace the exception
            logger.error(f"Error processing aggregated data: {e}")
            span.record_exception(e)
            span.set_status("ERROR")
            raise e
