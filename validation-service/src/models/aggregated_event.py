from pydantic import BaseModel, Field, model_validator
from uuid import UUID


class AggregatedEvent(BaseModel):
    """
    A data model representing an aggregated event in a transaction system.

    Attributes:
        total_amount (float): The total aggregated amount. Must be positive.
        event_id (UUID): A unique identifier for the event in UUID format.
        store_id (str): The identifier of the store where the transaction occurred.
        begin_stream_aggregator (str): The start timestamp of the aggregation period in ISO 8601 format.
        end_stream_aggregator (str): The end timestamp of the aggregation period in ISO 8601 format.
    """

    total_amount: float = Field(
        ..., description="Total aggregated amount, must be positive"
    )
    event_id: UUID = Field(
        ..., description="Unique identifier for the event (UUID format)"
    )
    store_id: str = Field(..., description="Identifier for the store")
    begin_stream_aggregator: str = Field(
        ..., description="Start timestamp of the aggregation period"
    )
    end_stream_aggregator: str = Field(
        ..., description="End timestamp of the aggregation period"
    )

    @model_validator(mode="before")
    def check_values(cls, values):
        """
        Validates the input values before creating an AggregatedEvent instance.

        Ensures that:
        - The total amount is positive.

        Args:
            values (dict): The raw input data to be validated.

        Returns:
            dict: The validated input data.

        Raises:
            ValueError: If the `total_amount` is not greater than 0.
        """
        total_amount = values.get("total_amount")
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        return values
