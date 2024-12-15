from fastapi import APIRouter, BackgroundTasks, Depends
from models.transaction_event import Transaction
from background_tasks import correct_transaction
from opentelemetry import trace
from logger_config import setup_logger
from utils import validate_basic_auth

# Initialize logger
logger = setup_logger()

# Initialize API router
router = APIRouter()


@router.post("/api/v1/pos/validate_transaction", status_code=200, tags=["Validation"])
async def validate_transaction(
    transaction: Transaction,
    background_tasks: BackgroundTasks,
    username: str = Depends(validate_basic_auth),
):
    """
    Endpoint to validate a point-of-sale (POS) transaction.

    This endpoint:
    - Validates the incoming transaction data.
    - Logs the transaction details and the authenticated username.
    - Adds a background task to correct the transaction if necessary.
    - Traces the operation using OpenTelemetry for observability.

    Args:
        transaction (Transaction): The transaction object to be validated.
        background_tasks (BackgroundTasks): FastAPI's background task manager to handle asynchronous tasks.
        username (str): Authenticated username extracted via Basic Auth.

    Returns:
        dict: A response dictionary containing:
            - `status` (str): Status of the validation process.
            - `transaction_id` (str): The unique identifier of the transaction.
            - `message` (str): A success message.

    Raises:
        Exception: If an error occurs during validation, the exception is logged and re-raised.

    OpenTelemetry Attributes:
        - `transaction.id`: The unique identifier for the transaction.
        - `transaction.store_id`: The store identifier associated with the transaction.
    """
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("validate_transaction") as span:
        # Set OpenTelemetry span attributes
        span.set_attribute("transaction.id", str(transaction.transaction_id))
        span.set_attribute("transaction.store_id", transaction.store_id)

        try:
            # Log received transaction details and username
            logger.info(
                f"Transaction received for validation by {username}: {transaction}"
            )

            # Add a background task for transaction correction
            background_tasks.add_task(correct_transaction, transaction)
            logger.info(
                f"Background task added for transaction ID {transaction.transaction_id}"
            )

            # Return success response
            return {
                "status": "success",
                "transaction_id": transaction.transaction_id,
                "message": "Transaction accepted",
            }
        except Exception as e:
            # Log and trace the exception
            logger.error(
                f"Error while validating transaction ID {transaction.transaction_id}: {e}"
            )
            span.record_exception(e)
            span.set_status("ERROR")
            raise e
