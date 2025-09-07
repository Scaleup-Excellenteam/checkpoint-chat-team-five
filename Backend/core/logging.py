import logging
import sys
from core.config import settings


def setup_logging():
    """Setup application logging"""
    logger = logging.getLogger("tspo")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    logger.handlers.clear()
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    
    return logger


logger = setup_logging()
