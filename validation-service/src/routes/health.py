from fastapi import APIRouter
from logger_config import setup_logger

# Initialize logger
logger = setup_logger()

# Initialize API router
router = APIRouter()


@router.get("/api/v1/health", status_code=200, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the application is running.

    This endpoint:
    - Confirms that the application is healthy and operational.
    - Logs each access to the health check endpoint for monitoring.

    Returns:
        dict: A response dictionary containing the health status and a message.
            - `status` (str): "ok" indicating the application is running.
            - `message` (str): A detailed message confirming the application's health.
    """
    # Log access to the endpoint
    logger.info("Health check endpoint accessed.")

    # Return the health status
    return {"status": "ok", "message": "The application is healthy and running."}
