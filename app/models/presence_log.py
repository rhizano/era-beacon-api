from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.session import Base
import uuid


class PresenceLog(Base):
    __tablename__ = "presence_logs"

    # Match exact database schema: id uuid DEFAULT gen_random_uuid() NOT NULL
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid(), index=True)
    # user_id text NOT NULL
    user_id = Column(Text, nullable=False, index=True)
    # beacon_id text NULL
    beacon_id = Column(Text, nullable=True, index=True)
    # "timestamp" timestamp NULL
    timestamp = Column(DateTime(timezone=False), nullable=True)  # Note: no timezone in your schema
    # latitude float8 NULL
    latitude = Column(Float, nullable=True)
    # longitude float8 NULL
    longitude = Column(Float, nullable=True)
    # signal_strength int4 NULL
    signal_strength = Column(Integer, nullable=True)
    # created_at timestamp DEFAULT now() NULL
    created_at = Column(DateTime(timezone=False), server_default=func.now(), nullable=True)
    # updated_at timestamp NULL
    updated_at = Column(DateTime(timezone=False), nullable=True)

    # Foreign key constraint: CONSTRAINT presence_logs_beacon_id_fkey FOREIGN KEY (beacon_id) REFERENCES public.beacons(beacon_id)
    __table_args__ = (
        ForeignKey('beacons.beacon_id', name='presence_logs_beacon_id_fkey'),
    )
