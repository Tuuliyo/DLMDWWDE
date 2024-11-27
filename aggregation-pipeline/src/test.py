import bytewax.operators as op
from bytewax.connectors.stdio import StdOutSink
from bytewax.dataflow import Dataflow
from bytewax.testing import TestingSource
from datetime import timedelta, timezone
from bytewax.operators.windowing import EventClock, TumblingWindower
import bytewax.operators.windowing as windowing
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from bytewax.inputs import DynamicSource, StatelessSourcePartition
import json
from datetime import datetime
import requests
import queue
from solace_consumer import message_queue
from solace_consumer import SolaceConsumer

# Solace configuration
POS_TRANSACTION_CONFIG = {
    "solace.messaging.transport.host": "tcp://message-broker:55555",
    "solace.messaging.service.vpn-name": "default",
    "solace.messaging.authentication.scheme.basic.username": "testuser",
    "solace.messaging.authentication.scheme.basic.password": "Test1234!",
}
POS_QUEUE_NAME = "sale.pos.transaction.aggregation.service"

# Initialize Solace Consumer


# Thread-safe queue for buffering Solace messages
message_queue = queue.Queue(maxsize=100000)

class SolaceSourcePartition(StatelessSourcePartition):
    def next_batch(self):
        try:
            payload = message_queue.get(timeout=0.001)
            print(f"Fetched from queue: {payload}")
            return [payload]
        except queue.Empty:
            return []

    def next_awake(self):
        return None


class SolaceDynamicSource(DynamicSource):
    def build(self, step_id, worker_index, worker_count):
        return SolaceSourcePartition()


class ApiSinkPartition(StatelessSinkPartition):
    def write_batch(self, items):
        for item in items:
            print(f"Sending to API: {item}")
            send_to_api(item)

    def close(self):
        pass


class ApiDynamicSink(DynamicSink):
    def build(self, step_id, worker_index, worker_count):
        return ApiSinkPartition()

def send_to_api(aggregated_data):
    url = "http://traefik/validation-service/api/v1/pos/amount-per-store"
    try:
        response = requests.post(url, json=aggregated_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data: {e}")
        
solace_consumer = SolaceConsumer(POS_TRANSACTION_CONFIG, POS_QUEUE_NAME)


flow = Dataflow("aggregation-pipeline")

# Sample Data for Testing
sample_events = src_2 = [{
        "transaction_id": "335f21fb-538a-4f30-a868-2ed0e0e31a57",
        "timestamp": "2024-11-27T15:40:49Z",
        "store_id": "STORE_2",
        "cashier_id": "CASHIER_9",
        "items": [{"item_id": "dd308a50-943f-4893-8a2d-a79e7f04b80a", "name": "Wasser - 1.5L", "quantity": 4, "price_per_unit": 0.79, "total_price": 3.16}],
        "total_amount": 3.16,
        "payment_method": "credit_card",
        "payment_status": "success",
        "customer_id": "CUSTOMER_316",
        "loyalty_points_earned": 4,
        "receipt": {
            "receipt_id": "37ed85ac-d41e-4cde-8cc7-06c4bca9a68e",
            "date": "2024-11-02T19:24:20.201465Z",
            "total_amount": 3.16,
            "payment_method": "credit_card",
            "transaction_id": "f02e5673-6927-4b8a-ac82-0940ddb80952"
        }
    },
    {
        "transaction_id": "f02e5673-6927-db8a-ac82-0940ddb80952",
        "timestamp": "2024-11-27T15:40:50Z",
        "store_id": "STORE_1",
        "cashier_id": "CASHIER_7",
        "items": [{"item_id": "dd308a50-943f-4893-8a2d-a79e7f04b80a", "name": "Wasser - 1.5L", "quantity": 4, "price_per_unit": 0.79, "total_price": 3.16}],
        "total_amount": 3.16,
        "payment_method": "credit_card",
        "payment_status": "success",
        "customer_id": "CUSTOMER_316",
        "loyalty_points_earned": 4,
        "receipt": {
            "receipt_id": "37ed85ac-d41e-4cde-8cc7-06c4bca9a68e",
            "date": "2024-11-02T07:24:20.201465Z",
            "total_amount": 3.16,
            "payment_method": "credit_card",
            "transaction_id": "f02e5673-6927-4b8a-ac82-0940ddb80952"
        }
    },
    {
        "transaction_id": "f02e5673-6927-4b8a-ac8c-0940ddb80953",
        "timestamp": "2024-11-27T15:40:50Z",
        "store_id": "STORE_1",
        "cashier_id": "CASHIER_0",
        "items": [{"item_id": "dd308a50-943f-4893-8a2d-a79e7f04b80a", "name": "Wasser - 1.5L", "quantity": 4, "price_per_unit": 0.79, "total_price": 3.16}],
        "total_amount": 3.16,
        "payment_method": "credit_card",
        "payment_status": "success",
        "customer_id": "CUSTOMER_316",
        "loyalty_points_earned": 4,
        "receipt": {
            "receipt_id": "37ed85ac-d41e-4cde-8cc7-06c4bca9a68e",
            "date": "2024-11-02T07:24:20.201465Z",
            "total_amount": 3.16,
            "payment_method": "credit_card",
            "transaction_id": "f02e5673-6927-4b8a-ac82-0940ddb80952"
        }
    },
    {
        "transaction_id": "f02e5673-d927-4b8a-ac82-0940ddb80959",
        "timestamp": "2024-11-27T15:40:50Z",
        "store_id": "STORE_2",
        "cashier_id": "CASHIER_7",
        "items": [{"item_id": "dd308a50-943f-4893-8a2d-a79e7f04b80a", "name": "Wasser - 1.5L", "quantity": 4, "price_per_unit": 0.79, "total_price": 3.16}],
        "total_amount": 3.16,
        "payment_method": "credit_card",
        "payment_status": "success",
        "customer_id": "CUSTOMER_316",
        "loyalty_points_earned": 4,
        "receipt": {
            "receipt_id": "37ed85ac-d41e-4cde-8cc7-06c4bca9a68e",
            "date": "2024-11-27T15:40:55.927199Z",
            "total_amount": 3.16,
            "payment_method": "credit_card",
            "transaction_id": "f02e5673-6927-4b8a-ac82-0940ddb80952"
        }
    }
    ,
    {
        "transaction_id": "f02ed673-6927-4b8a-ac82-0940ddb80959",
        "timestamp": "2024-11-27T15:40:41Z",
        "store_id": "STORE_2",
        "cashier_id": "CASHIER_7",
        "items": [{"item_id": "dd308a50-943f-4893-8a2d-a79e7f04b80a", "name": "Wasser - 1.5L", "quantity": 4, "price_per_unit": 0.79, "total_price": 3.16}],
        "total_amount": 3.16,
        "payment_method": "credit_card",
        "payment_status": "success",
        "customer_id": "CUSTOMER_316",
        "loyalty_points_earned": 4,
        "receipt": {
            "receipt_id": "37ed85ac-d41e-4cde-8cc7-06c4bca9a68e",
            "date": "2024-11-27T15:40:55.927199Z",
            "total_amount": 3.16,
            "payment_method": "credit_card",
            "transaction_id": "f02e5673-6927-4b8a-ac82-0940ddb80952"
        }
    }
]

# Deserialize JSON events into a Python dictionary
def deserialize_message(event: str):
    try:
        return json.loads(event)
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return None

# Define Timestamp Extraction Function
def extract_timestamp(timestamp_str):
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

# Accumulator Functions
def accumulator_builder():
    return {
        "total_amount": 0.0,
        "min_timestamp": None,
        "max_timestamp": None
    }

def aggregate_sales(accumulator, event):
    amount = event['total_amount']
    event_time = extract_timestamp(event['timestamp'])
    
    accumulator["total_amount"] += amount
    
    # Update min_timestamp
    if accumulator["min_timestamp"] is None or event_time < accumulator["min_timestamp"]:
        accumulator["min_timestamp"] = event_time
    
    # Update max_timestamp
    if accumulator["max_timestamp"] is None or event_time > accumulator["max_timestamp"]:
        accumulator["max_timestamp"] = event_time
    
    return accumulator

def merger(acc1, acc2):
    return {
        "total_amount": acc1["total_amount"] + acc2["total_amount"],
        "min_timestamp": min(
            acc1["min_timestamp"] or acc2["min_timestamp"],
            acc2["min_timestamp"] or acc1["min_timestamp"]
        ),
        "max_timestamp": max(
            acc1["max_timestamp"] or acc2["max_timestamp"],
            acc2["max_timestamp"] or acc1["max_timestamp"]
        )
    }

# Input Stream
#stream = op.input("input", flow, TestingSource(sample_events))
stream = op.input("solace_input", flow, SolaceDynamicSource())

# Deserialize Events
deserialized_events = op.map("deserialize", stream, deserialize_message)

# Filter None Events
valid_events = op.filter("valid_events", deserialized_events, lambda event: event is not None)


# Key Events by Store ID
keyed_events = op.key_on("key_by_store", valid_events, lambda x: x["store_id"])

# Clock and Window Configuration
#align_to_start = datetime.now(timezone.utc)
align_to_start = datetime(2024, 11, 15, 15, 40, 40, tzinfo=timezone.utc)
clock = EventClock(
    lambda e: extract_timestamp(e["timestamp"]),
    wait_for_system_duration=timedelta(seconds=0)
)
windower = TumblingWindower(length=timedelta(seconds=10), align_to=align_to_start) 

# Aggregation with fold_window
aggregated_events = windowing.fold_window(
    "aggregate_by_store",
    keyed_events,
    clock=clock,
    windower=windower,
    builder=accumulator_builder,
    folder=aggregate_sales,
    merger=merger
)

# Transform the aggregated events to the desired format
def format_aggregated_event(item):
    key, (window, accumulator) = item
    accumulator['store_id'] = key
    accumulator['begin_stream_aggregator'] = accumulator['min_timestamp'].isoformat() if accumulator['min_timestamp'] else None
    accumulator['end_stream_aggregator'] = accumulator['max_timestamp'].isoformat() if accumulator['max_timestamp'] else None
    # Remove raw timestamps from accumulator if desired
    del accumulator['min_timestamp']
    del accumulator['max_timestamp']
    return accumulator

formatted_events = op.map("format_in_event_structure", aggregated_events.down, format_aggregated_event)

# Output
#op.output("out", aggregated_events.down, StdOutSink())
op.output("api_output", formatted_events, ApiDynamicSink())

