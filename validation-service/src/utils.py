from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from logger_config import setup_logger

# Initialize logger
logger = setup_logger()

# Initialize Basic Auth security schema
security = HTTPBasic()


def validate_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Validate Basic Auth credentials against environment variables.

    This function validates HTTP Basic Auth credentials by dynamically constructing
    environment variable names based on the provided username. It checks the credentials
    against the expected username and password stored in environment variables.

    Args:
        credentials (HTTPBasicCredentials): The HTTP Basic Auth credentials provided by the client.

    Returns:
        str: The username if the credentials are valid.

    Raises:
        HTTPException: 
            - Status code 500: If the server is missing the expected environment variables for credentials.
            - Status code 401: If the provided credentials are invalid.

    Logic:
        1. Extracts the service name from the username (before the first `_`) and replaces hyphens with underscores.
        2. Constructs environment variable names for the username and password using the service name.
        3. Validates the provided credentials against these environment variables.

    Example:
        If the username is `validation_service`, the function expects environment variables:
        - `VALIDATION_SERVICE_USERNAME`
        - `VALIDATION_SERVICE_PASSWORD`
    """
    # Extract the service name from the username
    service_name = credentials.username.split("_", 1)[0].replace("-", "_")

    # Dynamically construct the environment variable names for username and password
    expected_username = os.getenv(f"{service_name.upper()}_USERNAME")
    expected_password = os.getenv(f"{service_name.upper()}_PASSWORD")

    # Check if the expected credentials are available in the environment
    if not (expected_username and expected_password):
        logger.error(f"Missing credentials for service: {service_name}")
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error: Missing credentials for {service_name}",
        )

    # Validate the provided credentials
    if (
        credentials.username != expected_username
        or credentials.password != expected_password
    ):
        logger.warning(
            f"Invalid credentials provided for service: {service_name} by user {credentials.username}"
        )
        raise HTTPException(status_code=401, detail="Invalid credentials")

    logger.info(f"Successfully authenticated user: {credentials.username}")
    return credentials.username
