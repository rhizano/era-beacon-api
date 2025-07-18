from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base
import uuid


class PresenceLog(Base):
    __tablename__ = "presence_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(String, nullable=False, index=True)
    beacon_id = Column(String, nullable=True, index=True)  # Allow NULL for flexibility
    timestamp = Column(DateTime(timezone=True), nullable=True)  # Allow NULL timestamps
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    signal_strength = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationship
    beacon = relationship("Beacon", back_populates="presence_logs", foreign_keys=[beacon_id])
