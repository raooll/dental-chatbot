# app/booking/interface.py
from datetime import datetime, time, timedelta, date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from dateutil import parser as date_parser

from app.appointments.models import Appointment, AppointmentType, AppointmentStatus
from app.db.utils import with_db


BUSINESS_OPEN_HOUR = 8  # 08:00
BUSINESS_CLOSE_HOUR = 18  # 18:00


def _is_business_day(dt: datetime) -> bool:
    # Monday=0 ... Sunday=6 => allow 0..5 (Mon-Sat)
    return dt.weekday() <= 5


def _within_business_hours(start: datetime, end: datetime) -> bool:
    if not _is_business_day(start) or not _is_business_day(end):
        return False
    open_time = time(BUSINESS_OPEN_HOUR, 0)
    close_time = time(BUSINESS_CLOSE_HOUR, 0)
    return (
        (start.time() >= open_time)
        and (end.time() <= close_time)
        and (start.date() == end.date())
    )


def _overlaps(
    a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime
) -> bool:
    return (a_start < b_end) and (b_start < a_end)


@with_db
async def list_appointments_for_patient(
    patient_id: int, db: AsyncSession = None
) -> List[Appointment]:
    q = await db.execute(
        select(Appointment).where(Appointment.patient_id == patient_id)
    )
    return q.scalars().all()


@with_db
async def list_appointments_between(
    start_dt: datetime,
    end_dt: datetime,
    target_date: Optional[date] = None,
    db: AsyncSession = None,
) -> List[Appointment]:
    """
    Fetch appointments between start_dt and end_dt. Optionally filter by target_date column.
    """
    stmt = select(Appointment).where(
        and_(
            Appointment.start_time >= start_dt,
            Appointment.start_time < end_dt,
            Appointment.status == AppointmentStatus.SCHEDULED.value,
        )
    )
    if target_date:
        stmt = stmt.where(Appointment.target_date == target_date)

    q = await db.execute(stmt)
    return q.scalars().all()


@with_db
async def list_available_slots_for_date(
    target_date: date,
    slot_minutes: int = 30,
    db: AsyncSession = None,
) -> List[datetime]:
    """
    Return start datetimes for available slots on target_date.
    Considers business hours and existing scheduled appointments.
    """
    start_of_day = datetime.combine(target_date, time(BUSINESS_OPEN_HOUR, 0))
    end_of_day = datetime.combine(target_date, time(BUSINESS_CLOSE_HOUR, 0))

    # fetch scheduled appointments for that date
    appointments = await list_appointments_between(
        start_of_day, end_of_day, target_date=target_date, db=db
    )

    slot_delta = timedelta(minutes=slot_minutes)
    slots = []
    cur = start_of_day
    while cur + slot_delta <= end_of_day:
        candidate_start = cur
        candidate_end = cur + slot_delta

        conflict = any(
            _overlaps(candidate_start, candidate_end, appt.start_time, appt.end_time)
            for appt in appointments
        )

        if not conflict:
            slots.append(candidate_start)

        cur += slot_delta

    return slots


@with_db
async def book_appointment(
    patient_id: int,
    appointment_type: str,
    start_time_iso: Optional[str] = None,
    target_date: Optional[date] = None,
    duration_minutes: int = 30,
    notes: Optional[str] = None,
    db: AsyncSession = None,
) -> Appointment:
    """
    Book an appointment with optional target_date.
    """
    if start_time_iso:
        start_time = date_parser.parse(start_time_iso)
        if target_date is None:
            target_date = start_time.date()
    else:
        start_time = None

    duration = timedelta(minutes=duration_minutes)

    # Emergency: pick earliest slot today or target_date
    if appointment_type == AppointmentType.EMERGENCY.value:
        if start_time is None:
            if target_date is None:
                target_date = datetime.now().date()
            slots = await list_available_slots_for_date(
                target_date, slot_minutes=duration_minutes, db=db
            )
            if not slots:
                raise ValueError(f"No available emergency slots on {target_date}.")
            start_time = slots[0]

    if start_time is None:
        raise ValueError("start_time is required for non-emergency bookings.")

    end_time = start_time + duration

    if not _within_business_hours(start_time, end_time):
        raise ValueError(
            "Appointment must be within business hours Mon-Sat 08:00-18:00."
        )

    # check conflicts
    existing = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.status == AppointmentStatus.SCHEDULED.value,
                Appointment.start_time < end_time,
                Appointment.end_time > start_time,
            )
        )
    )
    if existing.scalars().first():
        raise ValueError("Requested time slot is not available due to conflict.")

    appt = Appointment(
        patient_id=patient_id,
        appointment_type=appointment_type,
        start_time=start_time,
        end_time=end_time,
        target_date=target_date,
        status=AppointmentStatus.SCHEDULED.value,
        notes=notes,
    )
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt


@with_db
async def cancel_appointment(appointment_id: int, db: AsyncSession = None) -> bool:
    q = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = q.scalars().first()
    if not appt:
        return False
    appt.status = AppointmentStatus.CANCELLED.value
    await db.commit()
    return True


@with_db
async def reschedule_appointment(
    appointment_id: int, new_start_iso: str, db: AsyncSession = None
) -> Appointment:
    q = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appt = q.scalars().first()
    if not appt:
        raise ValueError("Appointment not found")

    new_start = date_parser.parse(new_start_iso)
    new_end = new_start + (appt.end_time - appt.start_time)

    if not _within_business_hours(new_start, new_end):
        raise ValueError("New time must be within business hours Mon-Sat 08:00-18:00.")

    # check conflicts (exclude current appointment)
    q2 = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.id != appointment_id,
                Appointment.status == AppointmentStatus.SCHEDULED.value,
                Appointment.start_time < new_end,
                Appointment.end_time > new_start,
            )
        )
    )
    if q2.scalars().first():
        raise ValueError("Requested new time conflicts with existing appointment.")

    appt.start_time = new_start
    appt.end_time = new_end
    appt.target_date = new_start.date()
    await db.commit()
    await db.refresh(appt)
    return appt
