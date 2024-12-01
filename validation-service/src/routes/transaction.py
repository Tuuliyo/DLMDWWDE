from fastapi import APIRouter, BackgroundTasks
from models.transaction_event import Transaction
from background_tasks import correct_transaction
from opentelemetry import trace

router = APIRouter()

@router.post("/api/v1/pos/validate_transaction")
async def validate_transaction(
    transaction: Transaction, background_tasks: BackgroundTasks
):
    tracer = trace.get_tracer(__name__)  # Get tracer for custom spans

    with tracer.start_as_current_span("validate_transaction") as span:
        span.set_attribute("transaction.id", str(transaction.transaction_id))
        span.set_attribute("transaction.store_id", transaction.store_id)

        try:
            # Add the background task for more complex validation/corrections
            background_tasks.add_task(correct_transaction, transaction)
            return {
                "status": "success",
                "transaction_id": transaction.transaction_id,
                "message": "transaction accepted",
            }
        except Exception as e:
            span.record_exception(e)
            span.set_status("ERROR")
            raise e