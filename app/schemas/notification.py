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
