# app/patient_info/models.py
from sqlalchemy import Column, String, Date
from app.db.base_model import BaseModel


class Patient(BaseModel):
    __tablename__ = "patients"

    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)
    insurance_name = Column(String(100), nullable=True)
