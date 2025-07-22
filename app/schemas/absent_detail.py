from pydantic import BaseModel
from typing import Optional


class AbsentDetailRecord(BaseModel):
    """Schema for a single absent detail record from v_presence_tracking view."""
    store_id: Optional[str] = None
    store: Optional[str] = None
    location: Optional[str] = None
    employee_id: Optional[str] = None
    employee: Optional[str] = None
    shift_in: Optional[str] = None
    shift_out: Optional[str] = None
    last_detection: Optional[str] = None
    absent_duration: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "store_id": "ST001",
                "store": "Main Store",
                "location": "Downtown",
                "employee_id": "EMP001",
                "employee": "John Doe",
                "shift_in": "2025-07-22 09:00:00",
                "shift_out": "2025-07-22 18:00:00",
                "last_detection": "2025-07-22 10:30:00",
                "absent_duration": "07:30"
            }
        }
