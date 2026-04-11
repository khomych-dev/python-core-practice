import logging
import sys
from contextvars import ContextVar
import structlog

request_id_var: ContextVar[str] = ContextVar("request_id", default="unknown")


def add_request_id(_logger, _method_name, event_dict):
    event_dict["request_id"] = request_id_var.get()
    return event_dict


def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_request_id,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


setup_logging()
log = structlog.get_logger()
