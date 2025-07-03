from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.beacon import Beacon
from app.schemas.beacon import BeaconCreate, BeaconUpdate


class BeaconService:
    def __init__(self, db: Session):
        self.db = db

    def create_beacon(self, beacon_data: BeaconCreate) -> Beacon:
        """Create a new beacon."""
        # Check if beacon with this beacon_id already exists
        existing_beacon = self.db.query(Beacon).filter(Beacon.beacon_id == beacon_data.beacon_id).first()
        if existing_beacon:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Beacon with this beacon_id already exists"
            )
        
        db_beacon = Beacon(**beacon_data.dict())
        self.db.add(db_beacon)
        self.db.commit()
        self.db.refresh(db_beacon)
        
        return db_beacon

    def get_all_beacons(self) -> List[Beacon]:
        """Get all beacons."""
        return self.db.query(Beacon).all()

    def get_beacon_by_beacon_id(self, beacon_id: str) -> Beacon:
        """Get beacon by beacon_id."""
        beacon = self.db.query(Beacon).filter(Beacon.beacon_id == beacon_id).first()
        if not beacon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beacon not found"
            )
        return beacon

    def update_beacon(self, beacon_id: str, beacon_data: BeaconUpdate) -> Beacon:
        """Update an existing beacon."""
        beacon = self.get_beacon_by_beacon_id(beacon_id)
        
        # Update only provided fields
        update_data = beacon_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(beacon, field, value)
        
        self.db.commit()
        self.db.refresh(beacon)
        
        return beacon

    def delete_beacon(self, beacon_id: str) -> None:
        """Delete a beacon."""
        beacon = self.get_beacon_by_beacon_id(beacon_id)
        self.db.delete(beacon)
        self.db.commit()
