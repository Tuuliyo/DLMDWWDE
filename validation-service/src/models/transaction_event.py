from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from typing import List


class Item(BaseModel):
    item_id: str = Field(..., description="Unique identifier for the item")
    name: str = Field(..., description="Name of the item")
    quantity: int = Field(..., description="Quantity of the item, must be positive")
    price_per_unit: float = Field(
        ..., description="Price per unit of the item, must be positive"
    )
    total_price: float = Field(
        ..., description="Total price for the item, must be positive"
    )

    @model_validator(mode="before")
    def check_item_values(cls, values):
        quantity = values.get("quantity")
        price_per_unit = values.get("price_per_unit")
        total_price = values.get("total_price")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if price_per_unit <= 0:
            raise ValueError("Price per unit must be positive")
        if total_price <= 0:
            raise ValueError("Total price must be positive")
        return values


class Receipt(BaseModel):
    receipt_id: str = Field(..., description="Unique receipt identifier")
    date: str = Field(..., description="Date and time the receipt was generated")
    total_amount: float = Field(
        ..., description="Total amount for the receipt, must be positive"
    )
    payment_method: str = Field(
        ..., description="Method of payment used for the transaction"
    )
    transaction_id: str = Field(
        ..., description="Transaction identifier associated with the receipt"
    )

    @model_validator(mode="before")
    def check_total_amount(cls, values):
        total_amount = values.get("total_amount")
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        return values


class Transaction(BaseModel):
    transaction_id: UUID = Field(
        ..., description="Unique transaction identifier (UUID format)"
    )
    timestamp: str = Field(
        ..., description="Timestamp of the transaction in ISO 8601 format"
    )
    store_id: str = Field(
        ..., description="Store identifier, must be one of STORE_01 to STORE_10"
    )
    cashier_id: str = Field(
        ..., description="Cashier identifier, must be one of CASHIER_2 to CASHIER_8"
    )
    items: List[Item] = Field(..., description="List of items in the transaction")
    total_amount: float = Field(
        ..., description="Total amount of the transaction, must be positive"
    )
    payment_method: str = Field(
        ...,
        description="Payment method used, one of: credit_card, cash, debit_card, voucher",
    )
    payment_status: str = Field(
        ..., description="Payment status of the transaction, one of: success, failed"
    )
    customer_id: str = Field(..., description="Customer identifier for the transaction")
    loyalty_points_earned: int = Field(
        ..., description="Number of loyalty points earned, must be non-negative"
    )
    receipt: Receipt = Field(
        ..., description="Receipt information associated with the transaction"
    )

    @model_validator(mode="before")
    def check_transaction_values(cls, values):
        store_id = values.get("store_id")
        cashier_id = values.get("cashier_id")
        total_amount = values.get("total_amount")
        payment_method = values.get("payment_method")
        payment_status = values.get("payment_status")

        # Store ID check
        if (
            not store_id.startswith("STORE_")
            or not store_id[6:].isdigit()
            or not (1 <= int(store_id[6:]) <= 10)
        ):
            raise ValueError("Store ID must be in the format STORE_01 to STORE_10")

        # Cashier ID check
        if (
            not cashier_id.startswith("CASHIER_")
            or not cashier_id[8:].isdigit()
            or not (1 <= int(cashier_id[8:]) <= 8)
        ):
            raise ValueError("Cashier ID must be in the format CASHIER_2 to CASHIER_8")

        # Total amount check
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")

        # Payment method and status checks
        if payment_method not in ["credit_card", "cash", "debit_card", "voucher"]:
            raise ValueError(f"Invalid payment method: {payment_method}")
        if payment_status not in ["success", "failed"]:
            raise ValueError(f"Invalid payment status: {payment_status}")

        return values