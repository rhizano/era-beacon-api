from fastapi import APIRouter, Depends, HTTPException, status, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import logging
from app.database.session import get_db
from app.services.absent_detail_service import AbsentDetailService
from app.schemas.absent_detail import AbsentDetailRecord
from app.schemas.error import ErrorResponse
from app.core.security import verify_token

router = APIRouter(tags=["Absent Detail"])
security = HTTPBearer()
logger = logging.getLogger(__name__)


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
    
    logger.info(f"Received request for absent detail with employee_id: '{employee_id}'")
    
    # Validate employee_id parameter
    if not employee_id or not employee_id.strip():
        logger.warning(f"Invalid employee_id received: '{employee_id}'")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="employee_id query parameter is required and cannot be empty"
        )
    
    try:
        # Create service instance and get absent detail records
        absent_detail_service = AbsentDetailService(db)
        records = absent_detail_service.get_absent_detail_by_employee_id(employee_id.strip())
        
        logger.info(f"Service returned {len(records)} records for employee_id: '{employee_id}'")
        
        # Return 404 if no records found
        if not records:
            logger.warning(f"No records found for employee_id: '{employee_id}', returning 404")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No absent detail records found for employee_id: {employee_id}"
            )
        
        logger.info(f"Returning {len(records)} records for employee_id: '{employee_id}'")
        return records
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle any other unexpected errors
        logger.error(f"Unexpected error processing request for employee_id '{employee_id}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve absent detail records: {str(e)}"
        )


@router.get(
    "/debug-absent-detail",
    status_code=status.HTTP_200_OK,
    summary="Debug endpoint for absent detail troubleshooting",
    description="Temporary diagnostic endpoint to troubleshoot the v_presence_tracking view"
)
async def debug_absent_detail(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Debug endpoint to check v_presence_tracking view structure and data."""
    
    try:
        from sqlalchemy import text
        
        # Test 1: Check if view exists and get structure
        structure_query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'v_presence_tracking'
            ORDER BY ordinal_position
        """)
        
        structure_result = db.execute(structure_query)
        structure_rows = structure_result.fetchall()
        
        # Test 2: Get sample data from view
        sample_query = text("SELECT * FROM v_presence_tracking LIMIT 5")
        sample_result = db.execute(sample_query)
        sample_rows = sample_result.fetchall()
        
        # Test 3: Check for specific employee_id
        employee_query = text("SELECT DISTINCT \"Employee ID\" FROM v_presence_tracking WHERE \"Employee ID\" = '202201209'")
        employee_result = db.execute(employee_query)
        employee_rows = employee_result.fetchall()
        
        # Test 4: Get all unique employee IDs
        all_employees_query = text("SELECT DISTINCT \"Employee ID\" FROM v_presence_tracking ORDER BY \"Employee ID\" LIMIT 20")
        all_employees_result = db.execute(all_employees_query)
        all_employees_rows = all_employees_result.fetchall()
        
        return {
            "view_structure": [{"column": row[0], "type": row[1]} for row in structure_rows],
            "sample_data_count": len(sample_rows),
            "sample_data": [dict(zip([col[0] for col in structure_rows], row)) for row in sample_rows[:2]],
            "employee_202201209_found": len(employee_rows) > 0,
            "employee_202201209_data": [row[0] for row in employee_rows],
            "sample_employee_ids": [row[0] for row in all_employees_rows],
            "total_records_in_view": db.execute(text("SELECT COUNT(*) FROM v_presence_tracking")).scalar()
        }
        
    except Exception as e:
        logger.error(f"Debug query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug query failed: {str(e)}"
        )
