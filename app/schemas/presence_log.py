from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class PresenceLogBase(BaseModel):
    user_id: str
    beacon_id: Optional[str] = None  # Make beacon_id optional to handle NULL values
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    signal_strength: Optional[int] = None


class PresenceLogCreate(PresenceLogBase):
    timestamp: Optional[datetime] = None  # Allow timestamp to be set optionally

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user456",
                "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
                "timestamp": "2024-01-15T14:30:00Z",
                "latitude": 34.052235,
                "longitude": -118.243683,
                "signal_strength": -75
            }
        }


class PresenceLog(PresenceLogBase):
    id: uuid.UUID
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
                "user_id": "user456",
                "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
                "timestamp": "2024-01-15T14:30:00Z",
                "latitude": 34.052235,
                "longitude": -118.243683,
                "signal_strength": -75,
                "created_at": "2024-01-15T14:30:00Z"
            }
        }
