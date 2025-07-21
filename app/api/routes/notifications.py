from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.notification_service import NotificationService
from app.schemas.notification import NotifyToQleapRequest, NotifyToQleapResponse, NotifyAbsenceRequest, NotifyAbsenceResponse, NotificationDetail
from app.schemas.error import ErrorResponse
from app.core.security import verify_token

router = APIRouter(prefix="/notifications", tags=["Notifications"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Dependency to get current authenticated user."""
    return verify_token(credentials.credentials)


@router.post(
    "/notify-to-qleap",
    response_model=NotifyToQleapResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "Beacon not found or no app tokens available"},
        500: {"model": ErrorResponse, "description": "Failed to send notifications"}
    },
    summary="Send push notifications to Qleap for beacon detection",
    description="""
    Send push notifications to all registered app tokens associated with a specific beacon.
    
    This endpoint:
    1. Queries the beacons table for all app_tokens matching the provided beacon_id
    2. Sends push notifications to each app_token via the Qleap notification service
    3. Returns the number of successful notifications sent
    
    The notification contains:
    - Title: "Eraspace Member is Detected!"
    - Body: "Open Information" 
    - Link: "https://erabeacon-7e08e.web.app/"
    """,
    operation_id="notifyToQleap"
)
async def notify_to_qleap(
    request_data: NotifyToQleapRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Send push notifications to all app tokens associated with a beacon.
    
    Args:
        request_data: Contains email, phone, and beacon_id
        db: Database session
        current_user: Authenticated user
        
    Returns:
        NotifyToQleapResponse with success message and count of notifications sent
    """
    notification_service = NotificationService(db)
    return notification_service.notify_to_qleap(request_data)


@router.post(
    "/notify-absence",
    response_model=NotifyAbsenceResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        500: {"model": ErrorResponse, "description": "Database or notification service error"}
    },
    summary="Send absence notifications to employees exceeding threshold",
    description="""
    Send absence notifications to employees who have exceeded the specified duration threshold.
    
    This endpoint:
    1. Queries the v_presence_tracking view to find employees with duration_minutes >= threshold
    2. Retrieves Employee ID and Employee Token for matching records
    3. Sends FCM notifications to each employee with absence alert
    4. Returns summary of notifications sent and failed
    
    The notification contains:
    - Title: "No Presence Detected!"
    - Body: "Out of store range"
    - Data: Employee ID for tracking purposes
    """,
    operation_id="notifyAbsence"
)
async def notify_absence(
    request_data: NotifyAbsenceRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Send absence notifications to employees exceeding the duration threshold.
    
    Args:
        request_data: Contains the threshold in minutes
        db: Database session
        current_user: Authenticated user
        
    Returns:
        NotifyAbsenceResponse with detailed results of the notification process
    """
    notification_service = NotificationService(db)
    result = await notification_service.notify_absence(request_data.threshold)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result["message"]
        )
    
    return NotifyAbsenceResponse(**result)
