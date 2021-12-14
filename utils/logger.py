import logging
import os
import sys
from logging import handlers


def get_logger(log_folder: str,
               log_name: str,
               log_level: int = logging.DEBUG,
               max_logfile_size: int = 5) -> logging.Logger:
    # Get a logger
    log_file_path = os.path.join(log_folder, f"{log_name}.log")
    logger = logging.getLogger(log_name)
    logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Unique file handler
    handler = handlers.RotatingFileHandler(log_file_path, maxBytes=(1_000_000 * max_logfile_size), backupCount=7)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # Global file handler
    handler = handlers.RotatingFileHandler(os.path.join(log_folder, "main.log"),
                                           maxBytes=(1_000_000 * max_logfile_size),
                                           backupCount=7)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # Stdout handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
