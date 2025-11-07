# app/booking/models.py
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    func,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.base_model import BaseModel
import enum


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AppointmentType(str, enum.Enum):
    CLEANING = "cleaning"
    GENERAL = "general_checkup"
    EMERGENCY = "emergency"


class Appointment(BaseModel):
    __tablename__ = "appointments"

    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_type = Column(String(50), nullable=False)
    start_time = Column(DateTime(timezone=False), nullable=False, index=True)
    end_time = Column(DateTime(timezone=False), nullable=False)
    status = Column(String(50), nullable=False, default=AppointmentStatus.SCHEDULED.value)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    # optional relationship to Patient (read-only here)
    patient = relationship("Patient", backref="appointments", lazy="joined")
