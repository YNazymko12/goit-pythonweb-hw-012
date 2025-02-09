"""Utility API endpoints.

This module provides utility endpoints for the application, including:
- Health check endpoint to verify database connectivity
- Other utility functions for system monitoring and maintenance
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.database.db import get_db
from src.conf import messages

router = APIRouter(tags=["utils"])


@router.get("/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)) -> dict:
    """Check the health of the application and database connection.

    Performs a simple database query to ensure the database connection is working.
    This endpoint is useful for monitoring and health check systems.

    Args:
        db (AsyncSession): Database session dependency.

    Returns:
        dict: A message indicating the health status.

    Raises:
        HTTPException: If the database query fails (500) or returns unexpected results (500).
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=messages.DATABASE_ERROR_CONFIG_MESSAGE,
            )
        return {"message": messages.HEALTHCHECKER_MESSAGE}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=messages.DATABASE_ERROR_CONNECT_MESSAGE,
        )