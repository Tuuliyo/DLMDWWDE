from fastapi import APIRouter
from logger_config import setup_logger


logger = setup_logger()
router = APIRouter()


@router.get("/api/v1/health", status_code=200, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the application is running.
    """
    logger.info("Health check endpoint accessed.")
    return {"status": "ok", "message": "The application is healthy and running."}
