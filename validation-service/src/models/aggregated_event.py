from pydantic import BaseModel, Field, model_validator
from uuid import UUID

class AggregatedEvent(BaseModel):
    total_amount: float = Field(..., description="Total aggregated amount, must be positive")
    event_id: UUID = Field(..., description="Unique identifier for the event (UUID format)")
    store_id: str = Field(..., description="Identifier for the store")
    begin_stream_aggregator: str = Field(..., description="Start timestamp of the aggregation period")
    end_stream_aggregator: str = Field(..., description="End timestamp of the aggregation period")

    @model_validator(mode="before")
    def check_values(cls, values):
        total_amount = values.get("total_amount")
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        return values