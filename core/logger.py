# core/logger.py
import logging
from logging.handlers import RotatingFileHandler
import sys
from .settings import settings

def setup_logger():
    logger = logging.getLogger("SarabiLabs")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        )

        # Console Output
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)

        # Rotating File Output (Max 5MB per file, keeps 3 backups)
        log_path = settings.LOG_DIR / "sarabilabs.log"
        settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_path, maxBytes=5*1024*1024, backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

logger = setup_logger()