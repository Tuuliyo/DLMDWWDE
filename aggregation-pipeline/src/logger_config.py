import os
import logging

def setup_logger():
    """
    Sets up and configures a logger for the aggregation service.

    The logger writes error-level logs to both a file and the console. It ensures
    that the log directory exists before creating log files.

    Returns:
        logging.Logger: Configured logger instance for the aggregation service.
    """
    # Create a logger for the aggregation service
    logger = logging.getLogger("aggregation-service")
    logger.setLevel(logging.ERROR)  # Set the log level to ERROR

    # Define the directory for log files
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)  # Ensure the logs directory exists

    # Configure file handler for logging
    log_file_path = os.path.join(log_dir, "api_logs.log")
    file_handler = logging.FileHandler(log_file_path)  # Logs will be written to this file
    file_handler.setLevel(logging.ERROR)  # File handler logs only ERROR-level messages
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # Log format
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)  # Add file handler to the logger

    # Configure console handler for logging
    console_handler = logging.StreamHandler()  # Logs will also appear in the console
    console_handler.setLevel(logging.ERROR)  # Console handler logs only ERROR-level messages
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)  # Add console handler to the logger

    return logger
