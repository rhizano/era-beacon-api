from pydantic import BaseModel
from typing import Optional


class NotifyToQleapRequest(BaseModel):
    email: str
    phone: str
    beacon_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "member@example.com",
                "phone": "+1234567890",
                "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0"
            }
        }


class NotifyToQleapResponse(BaseModel):
    message: str
    notifications_sent: int
    beacon_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Notifications sent successfully",
                "notifications_sent": 2,
                "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0"
            }
        }


class NotifyAbsenceRequest(BaseModel):
    threshold: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "threshold": 30
            }
        }


class NotifyAbsenceResponse(BaseModel):
    success: bool
    message: str
    total_employees: int
    notifications_sent: int
    notifications_failed: int
    threshold_minutes: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Processed 5 employees",
                "total_employees": 5,
                "notifications_sent": 4,
                "notifications_failed": 1,
                "threshold_minutes": 30
            }
        }
