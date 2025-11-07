import asyncio
from datetime import date
from random import randint
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.patient_info.models import Patient
from app.db.database import AsyncSessionLocal  # ✅ use the session factory directly

fake = Faker()


async def create_patients(count: int, db: AsyncSession = None):
    """Create a given number of fake patient records."""
    # ✅ If no session provided, create one manually
    if db is None:
        async with AsyncSessionLocal() as db:
            return await _create_patients(count, db)
    else:
        return await _create_patients(count, db)


async def _create_patients(count: int, db: AsyncSession):
    """Internal helper that assumes a valid AsyncSession."""
    patients = []
    for _ in range(count):
        patient = Patient(
            full_name=fake.name(),
            phone_number=f"+91{randint(6000000000, 9999999999)}",
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            insurance_name=fake.company() if randint(0, 1) else None,
        )
        db.add(patient)
        patients.append(patient)

    await db.commit()
    print(f"✅ Created {count} patients successfully.")
    return patients


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed fake patient data.")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of fake patients to create (default: 10)",
    )
    args = parser.parse_args()

    asyncio.run(create_patients(args.count))
