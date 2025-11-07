# app/patient_info/models.py
from sqlalchemy import Column, Integer, String, Date
from app.db.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(15), nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)
    insurance_name = Column(String(100), nullable=True)
