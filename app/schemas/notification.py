from pydantic import BaseModel
from typing import Optional, List, Dict, Any


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


class NotificationDetail(BaseModel):
    employee_id: str
    request_curl: str
    response_code: int
    response_message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "202304676",
                "request_curl": "curl -X POST 'https://example.com/send-notification' \\\n  -H 'Content-Type: application/json' \\\n  -d '{\"token\":\"abc123...\",\"title\":\"No Presence Detected!\",\"body\":\"Out of store range\"}'",
                "response_code": 500,
                "response_message": "{\"error\":\"Failed to send notification\",\"details\":\"Requested entity was not found.\"}"
            }
        }


class NotifyAbsenceResponse(BaseModel):
    success: bool
    threshold_minutes: Optional[int] = None
    message: str
    total_employees: int
    notifications_sent: int
    notifications_failed: int
    notifications_detail: List[NotificationDetail] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "threshold_minutes": 30,
                "message": "Processed 2 employees",
                "total_employees": 2,
                "notifications_sent": 0,
                "notifications_failed": 2,
                "notifications_detail": [
                    {
                        "employee_id": "202304676",
                        "request_curl": "curl -X POST 'https://example.com/send-notification' \\\n  -H 'Content-Type: application/json' \\\n  -d '{\"token\":\"abc123...\",\"title\":\"No Presence Detected!\",\"body\":\"Out of store range\"}'",
                        "response_code": 500,
                        "response_message": "{\"error\":\"Failed to send notification\",\"details\":\"Requested entity was not found.\"}"
                    }
                ]
            }
        }
