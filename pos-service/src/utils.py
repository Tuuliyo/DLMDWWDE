import random
import uuid
import json
from datetime import datetime, timedelta


# Helper function to load data from JSON files
def load_json_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Load items list and payment methods from JSON files
items_list = load_json_data("src/examples/items.json")  # Adjust the path as needed
payment_methods = load_json_data(
    "src/examples/payment_methods.json"
)  # Adjust the path as needed


# Helper function to generate random product data
def generate_item():
    # Choose a random item from the list
    item = random.choice(items_list)

    # Randomly decide how many units of this item are sold (1 to 5 units)
    quantity = random.randint(1, 5)

    # Calculate the total price for the item
    total_price = round(item["price"] * quantity, 2)

    return {
        "item_id": str(uuid.uuid4()),  # Unique item ID
        "name": item["name"],
        "quantity": quantity,
        "price_per_unit": item["price"],
        "total_price": total_price,
    }


# Helper function to generate the main transaction structure
def generate_transaction():
    # Generate a list of random items (between 1 and 5 items)
    num_items = random.randint(1, 5)
    items = [generate_item() for _ in range(num_items)]

    # Calculate the total amount for the transaction
    total_amount = round(sum(item["total_price"] for item in items), 2)

    payment_method = random.choice(payment_methods)
    payment_status = (
        "success" if random.random() > 0.001 else "failure"
    )  # >99% success rate
    
    # Generate a random timestamp within the last 30 days
    timestamp = datetime.now() - timedelta(days=random.randint(0, 30))

    return {
        "transaction_id": str(uuid.uuid4()),  # Unique transaction ID
        "timestamp": timestamp.now().isoformat() + "Z",  # ISO 8601 format with Z for UTC
        "store_id": f"STORE_{random.randint(1, 10)}",  # Random store ID (STORE_1 to STORE_10)
        "store_id": "STORE_1",
        "cashier_id": f"CASHIER_{random.randint(1, 8)}",  # Random cashier ID (CASHIER_1 to CASHIER_8)
        "items": items,
        "total_amount": total_amount,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "customer_id": f"CUSTOMER_{random.randint(1, 500)}",  # Random customer ID
        "loyalty_points_earned": random.randint(0, 5),  # Random loyalty points earned
        "receipt": {
            "receipt_id": str(uuid.uuid4()),  # Unique receipt ID
            "date": timestamp.isoformat() + "Z",
            "total_amount": total_amount,
            "payment_method": payment_method,
            "transaction_id": str(
                uuid.uuid4()
            ),  # Different transaction ID for the receipt
        },
    }
