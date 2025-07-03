from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services.beacon_service import BeaconService
from app.schemas.beacon import Beacon, BeaconCreate, BeaconUpdate
from app.schemas.error import ErrorResponse
from app.core.security import verify_token

router = APIRouter(prefix="/beacons", tags=["Beacons"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Dependency to get current authenticated user."""
    return verify_token(credentials.credentials)


@router.get(
    "",
    response_model=List[Beacon],
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"}
    },
    summary="Get a list of all beacons",
    operation_id="getAllBeacons"
)
async def get_all_beacons(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a list of all beacons."""
    beacon_service = BeaconService(db)
    return beacon_service.get_all_beacons()


@router.post(
    "",
    response_model=Beacon,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        409: {"model": ErrorResponse, "description": "Beacon with this beacon_id already exists"}
    },
    summary="Create a new beacon",
    operation_id="createBeacon"
)
async def create_beacon(
    beacon_data: BeaconCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new beacon."""
    beacon_service = BeaconService(db)
    return beacon_service.create_beacon(beacon_data)


@router.get(
    "/{beacon_id}",
    response_model=Beacon,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Beacon not found"}
    },
    summary="Get a beacon by its beacon_id",
    operation_id="getBeaconById"
)
async def get_beacon_by_id(
    beacon_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a beacon by its beacon_id."""
    beacon_service = BeaconService(db)
    return beacon_service.get_beacon_by_beacon_id(beacon_id)


@router.put(
    "/{beacon_id}",
    response_model=Beacon,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Beacon not found"}
    },
    summary="Update an existing beacon",
    operation_id="updateBeacon"
)
async def update_beacon(
    beacon_id: str,
    beacon_data: BeaconUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update an existing beacon."""
    beacon_service = BeaconService(db)
    return beacon_service.update_beacon(beacon_id, beacon_data)


@router.delete(
    "/{beacon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Beacon not found"}
    },
    summary="Delete a beacon",
    operation_id="deleteBeacon"
)
async def delete_beacon(
    beacon_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a beacon."""
    beacon_service = BeaconService(db)
    beacon_service.delete_beacon(beacon_id)
    return None
