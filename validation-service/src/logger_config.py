import os
import logging

def setup_logger():
    """
    Configures and returns a logger for the validation service.

    - Ensures a directory for log files exists at `/app/logs`.
    - Logs messages to both a file (`api_logs.log`) and the console.
    - Uses the ERROR logging level for minimal output in production.

    Returns:
        logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger("validation-service")
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
