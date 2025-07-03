from pydantic import BaseModel
from typing import Optional
import uuid


class BeaconBase(BaseModel):
    beacon_id: str
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BeaconCreate(BeaconBase):
    pass

    class Config:
        json_schema_extra = {
            "example": {
                "beacon_id": "F2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
                "location_name": "Cafeteria Entrance",
                "latitude": 34.052235,
                "longitude": -118.243683
            }
        }


class BeaconUpdate(BaseModel):
    beacon_id: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "location_name": "Updated Main Entrance",
                "latitude": 34.052235,
                "longitude": -118.243683
            }
        }


class Beacon(BeaconBase):
    id: uuid.UUID

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "beacon_id": "E2C56DB5-DFFB-48D2-B060-D0F5A71096E0",
                "location_name": "Main Entrance",
                "latitude": 34.052235,
                "longitude": -118.243683
            }
        }
