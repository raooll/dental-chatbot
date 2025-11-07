import asyncio
import random
from datetime import datetime, timedelta, time, date
from faker import Faker
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.appointments.models import Appointment, AppointmentStatus
from app.patient_info.models import Patient

fake = Faker()


async def create_appointments(count: int):
    """Create a given number of fake appointment records spread over a week (Mon–Sat, 8 AM–6 PM)."""
    async with AsyncSessionLocal() as db:
        # Get some existing patients
        result = await db.execute(select(Patient.id))
        patient_ids = [row[0] for row in result.all()]

        if not patient_ids:
            print("⚠️ No patients found. Please seed patients first.")
            return []

        appointments = []
        today = datetime.now().date()
        # define a week window (today + 6 days)
        week_days = [
            today + timedelta(days=i)
            for i in range(7)
            if (today + timedelta(days=i)).weekday() != 6
        ]

        for _ in range(count):
            patient_id = random.choice(patient_ids)

            # pick a random weekday from the week_days list
            target_date = random.choice(week_days)

            # pick a time between 8 AM and 5 PM for start (so appointment doesn't exceed 6 PM)
            start_hour = random.randint(8, 17)
            start_minute = random.choice([0, 15, 30, 45])
            start_time = datetime.combine(target_date, time(start_hour, start_minute))

            duration_minutes = random.choice([30, 45, 60])
            end_time = start_time + timedelta(minutes=duration_minutes)

            # adjust end_time if it exceeds business close hour
            if end_time.time() > time(18, 0):
                end_time = datetime.combine(target_date, time(18, 0))
                start_time = end_time - timedelta(minutes=duration_minutes)

            appointment = Appointment(
                patient_id=patient_id,
                appointment_type=random.choice(
                    ["Checkup", "Cleaning", "Filling", "Consultation"]
                ),
                start_time=start_time,
                end_time=end_time,
                target_date=target_date,
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
