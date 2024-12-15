from fastapi import APIRouter, BackgroundTasks
from models.transaction_event import Transaction
from background_tasks import correct_transaction
from opentelemetry import trace
from logger_config import setup_logger
from fastapi import Depends
from utils import validate_basic_auth

logger = setup_logger()
router = APIRouter()


@router.post("/api/v1/pos/validate_transaction", status_code=200, tags=["Validation"])
async def validate_transaction(
    transaction: Transaction,
    background_tasks: BackgroundTasks,
    username: str = Depends(validate_basic_auth),
):
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("validate_transaction") as span:
        span.set_attribute("transaction.id", str(transaction.transaction_id))
        span.set_attribute("transaction.store_id", transaction.store_id)

        try:
            logger.info(
                f"Transaction received for validation by {username}: {transaction}"
            )
            background_tasks.add_task(correct_transaction, transaction)
            logger.info(
                f"Background task added for transaction ID {transaction.transaction_id}"
            )
            return {
                "status": "success",
                "transaction_id": transaction.transaction_id,
                "message": "Transaction accepted",
            }
        except Exception as e:
            logger.error(
                f"Error while validating transaction ID {transaction.transaction_id}: {e}"
            )
            span.record_exception(e)
            span.set_status("ERROR")
            raise e
