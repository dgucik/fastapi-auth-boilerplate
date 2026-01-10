import logging
import sys
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Logging filter to inject request ID into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Injects request_id from context var into the record."""
        record.request_id = request_id_var.get()
        return True


def setup_logging(log_level: str) -> None:
    """Configures application logging.

    Args:
        log_level: The logging level (e.g., 'INFO', 'DEBUG').
    """
    request_id_filter = RequestIdFilter()

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    for handler in logging.root.handlers:
        handler.addFilter(request_id_filter)

    logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
