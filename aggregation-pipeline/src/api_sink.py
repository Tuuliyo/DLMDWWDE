from opentelemetry.trace import StatusCode, SpanKind
from opentelemetry import trace
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from logger_config import setup_logger
from utils import send_to_api
import os

logger = setup_logger()
tracer = trace.get_tracer(__name__)


class ApiSinkPartition(StatelessSinkPartition):
    def write_batch(self, items):
        for item in items:
            logger.info(f"Sending to API: {item}")
            try:
                with tracer.start_as_current_span(
                    "send_event_to_api", kind=SpanKind.CLIENT
                ) as send_span:
                    send_span.set_attribute("http.method", "POST")
                    send_span.set_attribute(
                        "http.url",
                        f"{os.getenv('API_PROTOCOL')}://{os.getenv('API_HOST')}:{os.getenv('API_PORT')}/validation-service/api/v1/pos/amount-per-store",
                    )
                    send_span.set_attribute("event.id", item["event_id"])
                    send_span.set_attribute("store.id", item["store_id"])

                    send_to_api(item)

            except Exception as e:
                logger.error(f"Failed to send item {item}: {e}")
                send_span.set_status(StatusCode.ERROR)
                send_span.record_exception(e)

    def close(self):
        logger.info("Closing ApiSinkPartition")


class ApiDynamicSink(DynamicSink):
    def build(self, step_id, worker_index, worker_count):
        return ApiSinkPartition()

