# node/src/utils/logger.py
import logging
import sys

def get_logger(name):
    """Creates a configured logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers: # Avoid adding handlers multiple times
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger