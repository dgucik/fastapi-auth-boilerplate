import logging
import sys
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def setup_logging(log_level: str) -> None:
    request_id_filter = RequestIdFilter()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    for handler in logging.root.handlers:
        handler.addFilter(request_id_filter)

    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
