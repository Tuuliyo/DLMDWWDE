from fastapi import APIRouter, BackgroundTasks
from models.aggregated_event import AggregatedEvent
from opentelemetry import trace
from background_tasks import send_aggregations
from logger_config import setup_logger
from fastapi import Depends
from utils import validate_basic_auth

# Initialize logger
logger = setup_logger()
router = APIRouter()


@router.post("/api/v1/pos/amount-per-store", status_code=200, tags=["Aggregations"])
async def amount_per_store(
    aggregated_event: AggregatedEvent,
    background_tasks: BackgroundTasks,
    username: str = Depends(validate_basic_auth),  # Inject Basic Auth validation
):
    """
    Endpoint to receive aggregated data from Flink job.
    """
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("amount_per_store") as span:
        span.set_attribute("event.id", str(aggregated_event.event_id))
        span.set_attribute("event.store_id", aggregated_event.store_id)

        try:
            logger.info(
                f"User '{username}' received aggregated data: {aggregated_event}"
            )
            background_tasks.add_task(send_aggregations, aggregated_event)
            return {
                "status": "success",
                "message": "Aggregated data received successfully.",
            }
        except Exception as e:
            logger.error(f"Error processing aggregated data: {e}")
            span.record_exception(e)
            span.set_status("ERROR")
            raise e
