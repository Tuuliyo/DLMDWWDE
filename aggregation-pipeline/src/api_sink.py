from opentelemetry.trace import StatusCode, SpanKind
from opentelemetry import trace
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from logger_config import setup_logger
from utils import send_to_api
import os

# Initialize the logger and tracer
logger = setup_logger()
tracer = trace.get_tracer(__name__)

class ApiSinkPartition(StatelessSinkPartition):
    """
    A sink partition class responsible for sending events to an external API.

    Inherits from StatelessSinkPartition and processes batches of items by
    sending them to the API using the `send_to_api` utility function.
    """

    def write_batch(self, items):
        """
        Processes a batch of items and sends each item to the API.

        Args:
            items (list[dict]): A list of event data dictionaries to be sent.
        """
        for item in items:
            logger.info(f"Sending to API: {item}")
            try:
                # Start a span for tracing API requests
                with tracer.start_as_current_span(
                    "send_event_to_api", kind=SpanKind.CLIENT
                ) as send_span:
                    # Add tracing attributes for HTTP request details
                    send_span.set_attribute("http.method", "POST")
                    send_span.set_attribute(
                        "http.url",
                        f"{os.getenv('API_PROTOCOL')}://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/validation-service/api/v1/pos/amount-per-store",
                    )
                    send_span.set_attribute("event.id", item["event_id"])
                    send_span.set_attribute("store.id", item["store_id"])

                    # Send the event data to the API
                    send_to_api(item)

            except Exception as e:
                # Handle errors by logging and recording them in the tracing span
                logger.error(f"Failed to send item {item}: {e}")
                send_span.set_status(StatusCode.ERROR)
                send_span.record_exception(e)

    def close(self):
        """
        Closes the sink partition and performs cleanup if necessary.

        This method is called when the sink is being shut down.
        """
        logger.info("Closing ApiSinkPartition")


class ApiDynamicSink(DynamicSink):
    """
    A dynamic sink class for creating instances of ApiSinkPartition.

    This class defines the behavior of the sink and how to create partition
    instances for distributed processing.
    """

    def build(self, step_id, worker_index, worker_count):
        """
        Builds a new instance of ApiSinkPartition.

        Args:
            step_id (str): The ID of the pipeline step.
            worker_index (int): The index of the current worker.
            worker_count (int): The total number of workers.

        Returns:
            ApiSinkPartition: A new instance of the ApiSinkPartition class.
        """
        return ApiSinkPartition()
