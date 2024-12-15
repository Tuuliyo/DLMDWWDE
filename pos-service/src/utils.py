import random
import uuid
import json
from datetime import datetime, timedelta


def load_json_data(file_path):
    """
    Loads data from a JSON file.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list: The data loaded from the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Load items list and payment methods from JSON files
items_list = load_json_data("src/examples/items.json")
payment_methods = load_json_data("src/examples/payment_methods.json")


def generate_item():
    """
    Generates a random item for a transaction.

    - Selects a random item from the items list.
    - Calculates the total price based on a random quantity.

    Returns:
        dict: A dictionary containing item details, including:
            - item_id (str): A unique ID for the item.
            - name (str): The name of the item.
            - quantity (int): The quantity of the item sold.
            - price_per_unit (float): The price of a single unit.
            - total_price (float): The total price for the item.
    """
    item = random.choice(items_list)
    quantity = random.randint(1, 5)
    total_price = round(item["price"] * quantity, 2)

    return {
        "item_id": str(uuid.uuid4()),
        "name": item["name"],
        "quantity": quantity,
        "price_per_unit": item["price"],
        "total_price": total_price,
    }


def generate_transaction():
    """
    Generates a random POS transaction.

    - Generates a list of items for the transaction.
    - Calculates the total amount and assigns a random payment method.
    - Simulates a >99% success rate for payments.
    - Assigns random store, cashier, and customer IDs.
    - Includes a receipt with additional details.

    Returns:
        dict: A dictionary containing transaction details, including:
            - transaction_id (str): A unique transaction ID.
            - timestamp (str): The transaction timestamp in ISO 8601 format.
            - store_id (str): The ID of the store where the transaction occurred.
            - cashier_id (str): The ID of the cashier processing the transaction.
            - items (list): A list of items in the transaction.
            - total_amount (float): The total amount for the transaction.
            - payment_method (str): The payment method used.
            - payment_status (str): "success" or "failure".
            - customer_id (str): The ID of the customer.
            - loyalty_points_earned (int): The loyalty points earned by the customer.
            - receipt (dict): Receipt details, including:
                - receipt_id (str): A unique receipt ID.
                - date (str): The receipt date in ISO 8601 format.
                - total_amount (float): The total amount on the receipt.
                - payment_method (str): The payment method on the receipt.
                - transaction_id (str): A unique transaction ID for the receipt.
    """
    num_items = random.randint(1, 5)
    items = [generate_item() for _ in range(num_items)]
    total_amount = round(sum(item["total_price"] for item in items), 2)
    payment_method = random.choice(payment_methods)
    payment_status = "success" if random.random() > 0.001 else "failure"
    timestamp = datetime.now() - timedelta(days=random.randint(0, 30))

    return {
        "transaction_id": str(uuid.uuid4()),
        "timestamp": (timestamp.now() - timedelta(seconds=10)).isoformat() + "Z",
        "store_id": f"STORE_{random.randint(1, 10)}",
        "cashier_id": f"CASHIER_{random.randint(1, 8)}",
        "items": items,
        "total_amount": total_amount,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "customer_id": f"CUSTOMER_{random.randint(1, 500)}",
        "loyalty_points_earned": random.randint(0, 5),
        "receipt": {
            "receipt_id": str(uuid.uuid4()),
            "date": timestamp.isoformat() + "Z",
            "total_amount": total_amount,
            "payment_method": payment_method,
            "transaction_id": str(uuid.uuid4()),
        },
    }
