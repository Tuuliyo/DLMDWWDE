import json
from datetime import datetime
import uuid
import requests
from logger_config import setup_logger
import os

# Initialize logger
logger = setup_logger()


def deserialize_message(event: str):
    """
    Deserializes a JSON-formatted string into a Python dictionary.

    Args:
        event (str): The JSON-formatted string.

    Returns:
        dict or None: The deserialized dictionary if successful, otherwise None.
    """
    try:
        return json.loads(event)
    except json.JSONDecodeError:
        logger.error("Error decoding JSON")
        return None


def extract_timestamp(timestamp_str):
    """
    Extracts a datetime object from an ISO 8601-formatted timestamp string.

    Args:
        timestamp_str (str): The ISO 8601-formatted timestamp.

    Returns:
        datetime: The corresponding datetime object.
    """
    return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))


def accumulator_builder():
    """
    Creates an initial accumulator for sales aggregation.

    Returns:
        dict: A dictionary with initialized fields for aggregation.
    """
    return {"total_amount": 0.0, "min_timestamp": None, "max_timestamp": None}


def aggregate_sales(accumulator, event):
    """
    Aggregates sales data by updating the accumulator with the event details.

    Args:
        accumulator (dict): The current state of the accumulator.
        event (dict): The new event data to include in the aggregation.

    Returns:
        dict: The updated accumulator.
    """
    amount = event["total_amount"]
    event_time = extract_timestamp(event["timestamp"])

    # Update total amount
    accumulator["total_amount"] += amount

    # Update minimum timestamp
    if (
        accumulator["min_timestamp"] is None
        or event_time < accumulator["min_timestamp"]
    ):
        accumulator["min_timestamp"] = event_time

    # Update maximum timestamp
    if (
        accumulator["max_timestamp"] is None
        or event_time > accumulator["max_timestamp"]
    ):
        accumulator["max_timestamp"] = event_time

    return accumulator


def merger(acc1, acc2):
    """
    Merges two accumulators into one.

    Args:
        acc1 (dict): The first accumulator.
        acc2 (dict): The second accumulator.

    Returns:
        dict: The merged accumulator.
    """
    return {
        "total_amount": acc1["total_amount"] + acc2["total_amount"],
        "min_timestamp": min(
            acc1["min_timestamp"] or acc2["min_timestamp"],
            acc2["min_timestamp"] or acc1["min_timestamp"],
        ),
        "max_timestamp": max(
            acc1["max_timestamp"] or acc2["max_timestamp"],
            acc2["max_timestamp"] or acc1["max_timestamp"],
        ),
    }


def format_aggregated_event(item):
    """
    Formats aggregated sales data into the required structure.

    Args:
        item (tuple): A tuple containing the store key and (window, accumulator).

    Returns:
        dict: A dictionary with the formatted aggregated data.
    """
    key, (window, accumulator) = item
    accumulator["event_id"] = str(uuid.uuid4())
    accumulator["store_id"] = key
    accumulator["total_amount"] = round(accumulator["total_amount"], 2)
    accumulator["begin_stream_aggregator"] = (
        accumulator["min_timestamp"].isoformat()
        if accumulator["min_timestamp"]
        else None
    )
    accumulator["end_stream_aggregator"] = (
        accumulator["max_timestamp"].isoformat()
        if accumulator["max_timestamp"]
        else None
    )
    del accumulator["min_timestamp"]
    del accumulator["max_timestamp"]
    return accumulator


def send_to_api(aggregated_data):
    """
    Sends aggregated sales data to a remote API.

    Args:
        aggregated_data (dict): The data to be sent to the API.
    """
    url = f"{os.getenv('API_PROTOCOL')}://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/validation-service/api/v1/pos/amount-per-store"

    try:
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=aggregated_data,
            auth=(os.getenv("API_USERNAME"), os.getenv("API_PASSWORD")),
        )
        response.raise_for_status()
        logger.info(f"Data sent successfully: {aggregated_data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send data: {e}")
