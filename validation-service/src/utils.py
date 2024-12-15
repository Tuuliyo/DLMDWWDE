from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from logger_config import setup_logger

logger = setup_logger()
security = HTTPBasic()


def validate_basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Validate Basic Auth credentials based on service name.
    This function extracts the service name from the provided username, constructs
    the expected environment variable names for the username and password, and
    validates the provided credentials against these expected values.
    Args:
        credentials (HTTPBasicCredentials): The HTTP Basic Auth credentials provided by the client.
    Returns:
        str: The username if the credentials are valid.
    Raises:
        HTTPException: If the server configuration is missing the expected credentials (status code 500).
        HTTPException: If the provided credentials are invalid (status code 401).
    """
    """Validate Basic Auth credentials based on service name."""

    # Extract the service name from the username (all before '_') and replace hyphens with underscores.
    # This is done to match the environment variable naming convention.
    service_name = credentials.username.split("_", 1)[0].replace("-", "_")

    # Dynamically construct the environment variable names
    expected_username = os.getenv(f"{service_name.upper()}_USERNAME")
    expected_password = os.getenv(f"{service_name.upper()}_PASSWORD")

    # Check if credentials are configured in environment variables.
    # If either the username or password is missing, raise an HTTP 500 error indicating a server configuration issue.
    if not (expected_username and expected_password):
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error: Missing credentials for {service_name}",
        )
    # Validate the provided credentials by comparing the username and password
    # with the expected values retrieved from the environment variables.
    # If the credentials do not match, raise an HTTP 401 Unauthorized error.
    # Validate the provided credentials
    if (
        credentials.username != expected_username
        or credentials.password != expected_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return credentials.username
