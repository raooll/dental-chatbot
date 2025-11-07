# app/patient_info/interface.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import date
from app.db.utils import with_db
from app.patient_info.models import Patient


@with_db
async def add_patient(
    full_name: str,
    phone_number: str,
    date_of_birth: date,
    insurance_name: str | None = None,
    db: AsyncSession = None,
):
    new_patient = Patient(
        full_name=full_name,
        phone_number=phone_number,
        date_of_birth=date_of_birth,
        insurance_name=insurance_name,
    )
    db.add(new_patient)
    await db.commit()
    await db.refresh(new_patient)
    return new_patient


@with_db
async def get_patient_by_id(patient_id: int, db: AsyncSession = None):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalars().first()


@with_db
async def get_patient_by_phone(phone_number: str, db: AsyncSession = None):
    result = await db.execute(select(Patient).where(Patient.phone_number == phone_number))
    return result.scalars().first()


@with_db
async def list_patients(db: AsyncSession = None):
    result = await db.execute(select(Patient))
    return result.scalars().all()


@with_db
async def delete_patient(patient_id: int, db: AsyncSession = None):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalars().first()
    if patient:
        await db.delete(patient)
        await db.commit()
        return True
    return False
