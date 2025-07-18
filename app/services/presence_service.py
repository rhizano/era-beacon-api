from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.models.presence_log import PresenceLog
from app.models.beacon import Beacon
from app.schemas.presence_log import PresenceLogCreate
import uuid


class PresenceService:
    def __init__(self, db: Session):
        self.db = db

    def create_presence_log(self, presence_data: PresenceLogCreate) -> PresenceLog:
        """Create a new presence log entry."""
        # Verify that the beacon exists if beacon_id is provided
        if presence_data.beacon_id:
            beacon = self.db.query(Beacon).filter(Beacon.beacon_id == presence_data.beacon_id).first()
            if not beacon:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Beacon with provided beacon_id not found"
                )
        
        # Create presence log with current timestamp if not provided
        presence_dict = presence_data.dict()
        if 'timestamp' not in presence_dict:
            presence_dict['timestamp'] = datetime.utcnow()
        
        db_presence_log = PresenceLog(**presence_dict)
        self.db.add(db_presence_log)
        self.db.commit()
        self.db.refresh(db_presence_log)
        
        return db_presence_log

    def get_all_presence_logs(
        self,
        user_id: Optional[str] = None,
        beacon_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[PresenceLog]:
        """Get presence logs with optional filtering."""
        query = self.db.query(PresenceLog)
        
        # Apply filters
        if user_id:
            query = query.filter(PresenceLog.user_id == user_id)
        if beacon_id:
            query = query.filter(PresenceLog.beacon_id == beacon_id)
        if start_date:
            # Handle NULL timestamps by treating them as very old dates
            query = query.filter(
                (PresenceLog.timestamp >= start_date) | 
                (PresenceLog.timestamp.is_(None))
            )
        if end_date:
            # Handle NULL timestamps by treating them as very old dates
            query = query.filter(
                (PresenceLog.timestamp < end_date) | 
                (PresenceLog.timestamp.is_(None))
            )
        
        # Order by timestamp (NULL values last) and created_at
        query = query.order_by(
            PresenceLog.timestamp.desc().nullslast(),
            PresenceLog.created_at.desc()
        )
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        return query.all()

    def get_presence_log_by_id(self, log_id: str) -> PresenceLog:
        """Get presence log by ID."""
        try:
            log_uuid = uuid.UUID(log_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid UUID format"
            )
        
        presence_log = self.db.query(PresenceLog).filter(PresenceLog.id == log_uuid).first()
        if not presence_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Presence log not found"
            )
        return presence_log

    def delete_presence_log(self, log_id: str) -> None:
        """Delete a presence log."""
        presence_log = self.get_presence_log_by_id(log_id)
        self.db.delete(presence_log)
        self.db.commit()
