import asyncio
import random
from datetime import datetime, timedelta, time
from faker import Faker
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.appointments.models import Appointment
from app.patient_info.models import Patient
from app.appointments.models import AppointmentStatus  # if you defined it

fake = Faker()


async def create_appointments(count: int):
    """Create a given number of fake appointment records (Mon–Sat, 8 AM–6 PM)."""
    async with AsyncSessionLocal() as db:
        # Get some existing patients
        result = await db.execute(select(Patient.id))
        patient_ids = [row[0] for row in result.all()]

        if not patient_ids:
            print("⚠️ No patients found. Please seed patients first.")
            return []

        appointments = []
        for _ in range(count):
            patient_id = random.choice(patient_ids)

            # pick a random weekday (Mon–Sat)
            date = fake.date_between(start_date="-7d", end_date="+7d")
            while date.weekday() == 6:  # skip Sunday
                date = fake.date_between(start_date="-7d", end_date="+7d")

            # pick a time between 8 AM and 6 PM
            start_hour = random.randint(8, 17)
            start_minute = random.choice([0, 15, 30, 45])
            start_time = datetime.combine(date, time(start_hour, start_minute))

            duration_minutes = random.choice([30, 45, 60])
            end_time = start_time + timedelta(minutes=duration_minutes)

            appointment = Appointment(
                patient_id=patient_id,
                appointment_type=random.choice(["Checkup", "Cleaning", "Filling", "Consultation"]),
                start_time=start_time,
                end_time=end_time,
                status=AppointmentStatus.SCHEDULED.value
                if hasattr(AppointmentStatus, "SCHEDULED")
                else "scheduled",
                notes=fake.sentence(nb_words=6),
            )

            db.add(appointment)
            appointments.append(appointment)

        await db.commit()
        print(f"✅ Created {count} appointments successfully.")
        return appointments


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed fake appointment data.")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of fake appointments to create (default: 10)",
    )
    args = parser.parse_args()

    asyncio.run(create_appointments(args.count))
