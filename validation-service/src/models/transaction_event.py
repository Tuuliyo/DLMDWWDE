from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from typing import List


class Item(BaseModel):
    """
    Represents an individual item in a transaction.

    Attributes:
        item_id (str): Unique identifier for the item.
        name (str): Name of the item.
        quantity (int): Quantity of the item, must be positive.
        price_per_unit (float): Price per unit of the item, must be positive.
        total_price (float): Total price for the item, must be positive.
    """

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
        """
        Validates item values before instantiation.

        Ensures that:
        - Quantity, price per unit, and total price are all positive.

        Args:
            values (dict): Raw input values for the item.

        Returns:
            dict: Validated item values.

        Raises:
            ValueError: If any field is non-positive.
        """
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
    """
    Represents a receipt associated with a transaction.

    Attributes:
        receipt_id (str): Unique identifier for the receipt.
        date (str): Date and time the receipt was generated (ISO 8601 format).
        total_amount (float): Total amount for the receipt, must be positive.
        payment_method (str): Payment method used for the transaction.
        transaction_id (str): Identifier for the transaction associated with the receipt.
    """

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
        """
        Validates the total amount of the receipt.

        Ensures that:
        - Total amount is positive.

        Args:
            values (dict): Raw input values for the receipt.

        Returns:
            dict: Validated receipt values.

        Raises:
            ValueError: If total amount is non-positive.
        """
        total_amount = values.get("total_amount")
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        return values


class Transaction(BaseModel):
    """
    Represents a point-of-sale (POS) transaction.

    Attributes:
        transaction_id (UUID): Unique identifier for the transaction.
        timestamp (str): Timestamp of the transaction (ISO 8601 format).
        store_id (str): Identifier of the store (STORE_01 to STORE_10).
        cashier_id (str): Identifier of the cashier (CASHIER_1 to CASHIER_8).
        items (List[Item]): List of items in the transaction.
        total_amount (float): Total amount of the transaction, must be positive.
        payment_method (str): Payment method used (e.g., credit_card, cash).
        payment_status (str): Status of the payment (success or failed).
        customer_id (str): Identifier of the customer.
        loyalty_points_earned (int): Loyalty points earned, must be non-negative.
        receipt (Receipt): Receipt details associated with the transaction.
    """

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
        ..., description="Cashier identifier, must be one of CASHIER_1 to CASHIER_8"
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
        """
        Validates transaction values before instantiation.

        Ensures that:
        - Store ID and cashier ID are correctly formatted.
        - Total amount is positive.
        - Payment method and status are valid.

        Args:
            values (dict): Raw input values for the transaction.

        Returns:
            dict: Validated transaction values.

        Raises:
            ValueError: If any field contains invalid or out-of-range values.
        """
        store_id = values.get("store_id")
        cashier_id = values.get("cashier_id")
        total_amount = values.get("total_amount")
        payment_method = values.get("payment_method")
        payment_status = values.get("payment_status")

        if (
            not store_id.startswith("STORE_")
            or not store_id[6:].isdigit()
            or not (1 <= int(store_id[6:]) <= 10)
        ):
            raise ValueError("Store ID must be in the format STORE_01 to STORE_10")

        if (
            not cashier_id.startswith("CASHIER_")
            or not cashier_id[8:].isdigit()
            or not (1 <= int(cashier_id[8:]) <= 8)
        ):
            raise ValueError("Cashier ID must be in the format CASHIER_1 to CASHIER_8")

        if total_amount <= 0:
            raise ValueError("Total amount must be positive")

        if payment_method not in ["credit_card", "cash", "debit_card", "voucher"]:
            raise ValueError(f"Invalid payment method: {payment_method}")

        if payment_status not in ["success", "failed"]:
            raise ValueError(f"Invalid payment status: {payment_status}")

        return values
