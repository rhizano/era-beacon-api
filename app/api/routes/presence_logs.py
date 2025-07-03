from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database.session import get_db
from app.services.presence_service import PresenceService
from app.schemas.presence_log import PresenceLog, PresenceLogCreate
from app.schemas.error import ErrorResponse
from app.core.security import verify_token

router = APIRouter(prefix="/presence-logs", tags=["Presence Logs"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Dependency to get current authenticated user."""
    return verify_token(credentials.credentials)


@router.post(
    "",
    response_model=PresenceLog,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Beacon not found"}
    },
    summary="Log a user's presence near a beacon",
    operation_id="createPresenceLog"
)
async def create_presence_log(
    presence_data: PresenceLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Log a user's presence near a beacon."""
    presence_service = PresenceService(db)
    return presence_service.create_presence_log(presence_data)


@router.get(
    "",
    response_model=List[PresenceLog],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"}
    },
    summary="Get a list of all presence logs",
    operation_id="getAllPresenceLogs"
)
async def get_all_presence_logs(
    user_id: Optional[str] = Query(None, description="Filter logs by user ID"),
    beacon_id: Optional[str] = Query(None, description="Filter logs by beacon ID"),
    start_date: Optional[datetime] = Query(None, description="Filter logs from a specific timestamp (inclusive)"),
    end_date: Optional[datetime] = Query(None, description="Filter logs up to a specific timestamp (exclusive)"),
    limit: int = Query(100, ge=1, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a list of presence logs with optional filtering."""
    presence_service = PresenceService(db)
    return presence_service.get_all_presence_logs(
        user_id=user_id,
        beacon_id=beacon_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{id}",
    response_model=PresenceLog,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Presence log not found"}
    },
    summary="Get a presence log by its ID",
    operation_id="getPresenceLogById"
)
async def get_presence_log_by_id(
    id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a presence log by its ID."""
    presence_service = PresenceService(db)
    return presence_service.get_presence_log_by_id(id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Presence log not found"}
    },
    summary="Delete a presence log by its ID",
    operation_id="deletePresenceLog"
)
async def delete_presence_log(
    id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a presence log by its ID."""
    presence_service = PresenceService(db)
    presence_service.delete_presence_log(id)
    return None
