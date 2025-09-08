import logging
import json
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from core.config import settings


_logger_instance = None


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "module": record.module,
        }
        return json.dumps(payload, ensure_ascii=False)


def setup_logging():
    """Setup application logging (singleton). Writes JSON lines to root/Data/app.log"""
    global _logger_instance
    if _logger_instance is not None:
        return _logger_instance

    logger = logging.getLogger("tspo")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    logger.handlers.clear()

    # Console handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (JSON) at repo root / Data / app.log
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "Data"
    data_dir.mkdir(parents=True, exist_ok=True)
    log_path = data_dir / "app.log"
    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    logger.propagate = False

    _logger_instance = logger
    return logger


logger = setup_logging()
