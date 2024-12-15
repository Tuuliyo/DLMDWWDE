import os
import logging

def setup_logger():
    """
    Sets up a logger for the aggregation service with both file and console handlers.

    - Ensures a `/app/logs` directory exists for storing log files.
    - Logs messages to both a file and the console.
    - Uses the ERROR logging level by default for minimal output in production.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("aggregation-service")
    logger.setLevel(logging.ERROR)

    # Ensure the logs directory exists
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)

    # File handler for logging to a file
    log_file_path = os.path.join(log_dir, "api_logs.log")
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler for logging to the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
