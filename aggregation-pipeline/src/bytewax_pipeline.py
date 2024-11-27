from bytewax.dataflow import Dataflow
from bytewax.inputs import DynamicSource, StatelessSourcePartition
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from bytewax.operators.windowing import EventClock, TumblingWindower
import bytewax.operators.windowing as windowing
import bytewax.operators as op
from datetime import timedelta, timezone, datetime as dt
from dateutil.parser import parse as parse_iso
import json
import requests
import logging
from solace_consumer import message_queue
import queue

# Bytewax Input: Solace Dynamic Source
class SolaceSourcePartition(StatelessSourcePartition):
    def next_batch(self):
        try:
            payload = message_queue.get(timeout=0.5)
            return [payload]
        except queue.Empty:
            return []

    def next_awake(self):
        return None


class SolaceDynamicSource(DynamicSource):
    def build(self, step_id, worker_index, worker_count):
        return SolaceSourcePartition()


# Bytewax Output: Send to API
class ApiSinkPartition(StatelessSinkPartition):
    def write_batch(self, items):
        for item in items:
            logging.info(f"Sending to API: {item}")
            send_to_api(item)

    def close(self):
        pass


class ApiDynamicSink(DynamicSink):
    def build(self, step_id, worker_index, worker_count):
        return ApiSinkPartition()


def deserialize_message(message):
    try:
        return json.loads(message)
    except json.JSONDecodeError:
        logging.error(f"Failed to decode message: {message}")
        return None


def extract_store_key(event):
    return event["store_id"], event


def extract_timestamp(event):
    timestamp = parse_iso(event["timestamp"])
    return int(timestamp.timestamp() * 1000)


def aggregate_sales(key, events):
    store_id, _ = key
    total_sales = sum(event["total_amount"] for event in events)
    return {
        "store_id": store_id,
        "total_sales": total_sales,
        "window_start": min(events, key=extract_timestamp)["timestamp"],
        "window_end": max(events, key=extract_timestamp)["timestamp"],
    }


def send_to_api(aggregated_data):
    url = "http://traefik/validation-service/api/v1/pos/amount-per-store"
    try:
        response = requests.post(url, json=aggregated_data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send data: {e}")


# Define the pipeline
flow = Dataflow("pos-transaction-aggregation")
input_stream = op.input("solace_input", flow, SolaceDynamicSource())
deserialized_events = op.map("deserialize", input_stream, deserialize_message)
valid_events = op.filter("valid_events", deserialized_events, lambda event: event is not None)
keyed_events = op.map("key_by_store", valid_events, extract_store_key)

align_to_start = dt.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
aggregated_events = windowing.reduce_window(
    "aggregate_by_store",
    keyed_events,
    EventClock(lambda event: extract_timestamp(event), timedelta(seconds=5)),
    TumblingWindower(length=timedelta(seconds=5), align_to=align_to_start),
    aggregate_sales,
)

event_stream = op.map("remove_key", aggregated_events.down, lambda x: x[1])
op.output("api_output", event_stream, ApiDynamicSink())
