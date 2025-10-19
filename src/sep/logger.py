import logging
from typing import Optional

# Global configuration
_DEFAULT_LOG_LEVEL = logging.INFO
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: Optional[str] = None, level: Optional[int] = None) -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name: Optional logger name (typically __name__).
        level: Optional logging level (e.g., logging.DEBUG).
               If not provided, uses the global default.

    Usage:
        from logger import setup_logger
        log = setup_logger(__name__)
        log.info("Something happened")
    """
    logger = logging.getLogger(name)

    # Only configure the root handler once
    if not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(_DEFAULT_LOG_LEVEL)

    # If a specific level is requested, override it
    if level is not None:
        logger.setLevel(level)

    return logger


def set_global_log_level(level: int):
    """
    Sets the global log level for the root logger.

    Example:
        from logger import set_global_log_level
        set_global_log_level(logging.DEBUG)
    """
    logging.getLogger().setLevel(level)
