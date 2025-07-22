from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any
import logging
from app.schemas.absent_detail import AbsentDetailRecord

# Set up logging
logger = logging.getLogger(__name__)


class AbsentDetailService:
    """Service for handling absent detail operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_absent_detail_by_employee_id(self, employee_id: str) -> List[AbsentDetailRecord]:
        """
        Get absent detail records for a specific employee from v_presence_tracking view.
        
        Args:
            employee_id: The employee ID to filter by
            
        Returns:
            List of AbsentDetailRecord objects
            
        Raises:
            Exception: If database query fails
        """
        try:
            logger.info(f"Querying absent detail for employee_id: {employee_id}")
            
            # Execute the specific SQL query as requested
            query = text("""
                SELECT "Store ID", "Store", "Location", "Employee ID", "Employee", 
                       "Shift In", "Shift Out", "Last Detection", "Absent Duration (Hour:Minute)"
                FROM v_presence_tracking
                WHERE "Employee ID" = :employee_id
            """)
            
            logger.info(f"Executing query with parameter employee_id: '{employee_id}'")
            result = self.db.execute(query, {"employee_id": employee_id})
            rows = result.fetchall()
            
            logger.info(f"Query returned {len(rows)} rows")
            
            # Log the first few rows for debugging
            if rows:
                for i, row in enumerate(rows[:3]):  # Log first 3 rows max
                    logger.info(f"Row {i}: {dict(zip(['Store ID', 'Store', 'Location', 'Employee ID', 'Employee', 'Shift In', 'Shift Out', 'Last Detection', 'Absent Duration'], row))}")
            else:
                logger.warning(f"No rows found for employee_id: {employee_id}")
                
                # Let's also try a more permissive query to see if the employee exists at all
                test_query = text("SELECT DISTINCT \"Employee ID\" FROM v_presence_tracking LIMIT 10")
                test_result = self.db.execute(test_query)
                test_rows = test_result.fetchall()
                logger.info(f"Sample employee IDs in view: {[row[0] for row in test_rows]}")
            
            # Convert rows to list of AbsentDetailRecord objects
            records = []
            for row in rows:
                record = AbsentDetailRecord(
                    store_id=row[0],
                    store=row[1],
                    location=row[2],
                    employee_id=row[3],
                    employee=row[4],
                    shift_in=str(row[5]) if row[5] is not None else None,
                    shift_out=str(row[6]) if row[6] is not None else None,
                    last_detection=str(row[7]) if row[7] is not None else None,
                    absent_duration=row[8]
                )
                records.append(record)
            
            logger.info(f"Converted {len(records)} records to AbsentDetailRecord objects")
            return records
            
        except Exception as e:
            logger.error(f"Database query failed for employee_id {employee_id}: {str(e)}")
            raise Exception(f"Failed to query absent detail data: {str(e)}")
