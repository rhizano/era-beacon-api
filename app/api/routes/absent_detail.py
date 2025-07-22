from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.services.absent_detail_service import AbsentDetailService
from app.schemas.absent_detail import AbsentDetailRecord
from app.schemas.error import ErrorResponse
from app.core.security import verify_token

router = APIRouter(tags=["Absent Detail"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Dependency to get current authenticated user."""
    return verify_token(credentials.credentials)


@router.get(
    "/absent-detail",
    response_model=List[AbsentDetailRecord],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Missing or invalid employee_id parameter"},
        401: {"model": ErrorResponse, "description": "Authentication required"},
        403: {"model": ErrorResponse, "description": "Insufficient permissions"},
        404: {"model": ErrorResponse, "description": "No records found for the specified employee_id"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    },
    summary="Get absent detail records for a specific employee",
    description="""
    Retrieve absent detail records for a specific employee from the v_presence_tracking view.
    
    This endpoint:
    1. Accepts an employee_id as a query parameter
    2. Executes a SELECT query against the v_presence_tracking view
    3. Filters results by the provided employee_id
    4. Returns matching records as a JSON array
    
    The query executed is:
    ```sql
    SELECT "Store ID", "Store", "Location", "Employee ID", "Employee", 
           "Shift In", "Shift Out", "Last Detection", "Absent Duration (Hour:Minute)"
    FROM v_presence_tracking
    WHERE "Employee ID" = :employee_id;
    ```
    
    **Query Parameter:**
    - employee_id: The ID of the employee to get absent details for
    
    **Returns:**
    - Array of absent detail records containing store info, employee details, shift times, and absence duration
    - Empty array if no records found for the employee_id
    """,
    operation_id="getAbsentDetail"
)
async def get_absent_detail(
    employee_id: str = Query(..., description="The employee ID to get absent details for"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get absent detail records for a specific employee."""
    
    # Validate employee_id parameter
    if not employee_id or not employee_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="employee_id query parameter is required and cannot be empty"
        )
    
    try:
        # Create service instance and get absent detail records
        absent_detail_service = AbsentDetailService(db)
        records = absent_detail_service.get_absent_detail_by_employee_id(employee_id.strip())
        
        # Return 404 if no records found
        if not records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No absent detail records found for employee_id: {employee_id}"
            )
        
        return records
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve absent detail records: {str(e)}"
        )
