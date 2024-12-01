import os
import logging

def setup_logger():
    logger = logging.getLogger("aggregation-service")
    logger.setLevel(logging.ERROR)

    # Ensure the logs directory exists
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)

    # File handler
    log_file_path = os.path.join(log_dir, "api_logs.log")
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
