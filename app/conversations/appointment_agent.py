# app/conversations/agent.py

from dataclasses import dataclass
from typing import Dict, Optional
from datetime import date, datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext

from app.db.database import get_db
from app.patient_info.models import Patient
from app.appointments.models import Appointment, AppointmentType
from app.patient_info.interface import add_patient, get_patient_by_phone
from app.appointments.interface import (
    book_appointment,
    list_appointments_for_patient,
    list_available_slots_for_date,
)
from app.conversations.interface import escalate_conversation_to_admin, get_messages
from app.conversations.models import Conversation, SenderTypeEnum


import logfire

# configure logfire
logfire.configure(token="pylf_v1_us_fTkV82Y6y3RjYSnb9xYvfJYz5NZcWB1R7Pg7T0kl8Lgk")
logfire.instrument_pydantic_ai()
# ─────────────────────────────────────────────
# Dependencies
# ─────────────────────────────────────────────


@dataclass
class DentalDependencies:
    db: any
    conversation_id: Optional[int] = None
    patient: Optional[Patient] = None


# ─────────────────────────────────────────────
# Output schema (optional for structure)
# ─────────────────────────────────────────────


class DentalOutput(BaseModel):
    message: str = Field(..., description="The assistant's message to the patient")
    next_action: Optional[str] = Field(
        None,
        description="What the assistant plans to do next (e.g., find_patient, set_appointment, escalate_to_human)",
    )


# ─────────────────────────────────────────────
# Initialize the Agent
# ─────────────────────────────────────────────

dental_agent = Agent(
    model="google-gla:gemini-2.5-flash",
    deps_type=DentalDependencies,
    output_type=DentalOutput,
    instructions=(
        "You are a warm, conversational, and helpful **virtual dental assistant** "
        "helping patients at a dental clinic. Speak naturally, like a caring receptionist, "
        "using a friendly and empathetic tone. Keep responses short, human-like, and to the point — "
        "no robotic phrasing or formal disclaimers.\n\n"
        "### Conversational Style\n"
        "- Start with a friendly greeting (e.g., 'Hi there! How can I help you today?').\n"
        "- Use natural phrasing like 'Sure!', 'Of course!', 'Got it!', 'Let me check that for you.'\n"
        "- Show empathy if someone is anxious or unhappy.\n"
        "- Always use simple, polite language.\n\n"
        "### Core Workflow\n"
        "1. Ask for the patient’s **phone number** to identify them.\n"
        "2. If the patient exists, confirm their name and continue the conversation naturally.\n"
        "3. If they’re new, gently ask for their **full name**, **date of birth**, and **insurance provider**.\n"
        "4. Once you have the details, use `register_patient` to create their profile.\n"
        "5. Once the user details are there ask the user what kind of appointment does he want to book and provide possible appointment slots using "
        "5. Then help them **book an appointment** (Cleaning, General Checkup, Emergency) using `set_appointment`.\n"
        "6. If they seem frustrated or say things like 'I want to talk to a person', immediately use `escalate_to_human`.\n\n"
        "Always keep your messages kind, concise, and conversational."
    ),
)


# ─────────────────────────────────────────────
# Tools
# ─────────────────────────────────────────────


@dental_agent.tool
async def find_patient(
    ctx: RunContext[DentalDependencies],
    phone: str,
) -> Optional[str]:
    """Look up a patient by phone number."""
    db = ctx.deps.db
    patient = await get_patient_by_phone(db=db, phone_number=phone)
    if patient:
        conversation = await db.get(Conversation, ctx.deps.conversation_id)
        conversation.patient_id = patient.id

        await db.commit()
        await db.refresh(conversation)

        ctx.deps.patient = patient

        return f"Patient found: {patient.full_name}, DOB: {patient.date_of_birth}, Insurance: {patient.insurance_name}."
    else:
        return "No existing patient found with that phone number."


@dental_agent.tool
async def register_patient(
    ctx: RunContext[DentalDependencies],
    full_name: str,
    phone: str,
    dob: date,
    insurance_name: Optional[str] = None,
) -> str:
    """Register a new patient in the database."""
    print("Running register_patient")
    db = ctx.deps.db
    new_patient = await add_patient(
        db=db,
        full_name=full_name,
        phone_number=phone,
        date_of_birth=dob,
        insurance_name=insurance_name,
    )
    ctx.deps.patient = new_patient
    return f"New patient {full_name} registered successfully."


@dental_agent.tool
async def set_appointment(
    ctx: RunContext[DentalDependencies],
    appointment_type: str,
    target_date: date,
    preferred_time: str,
) -> str:
    """Book an appointment for the current patient on the given target_date."""
    db = ctx.deps.db
    active_conversation = await db.get(Conversation, ctx.deps.conversation_id)
    active_patient = await db.get(Patient, active_conversation.patient_id)

    if not active_conversation:
        return (
            "Please provide your phone number first so I can identify or register you."
        )

    # Combine target_date and preferred_time into a full datetime string
    start_time_str = f"{target_date.isoformat()} {preferred_time}"

    try:
        appointment = await book_appointment(
            patient_id=active_patient.id,
            appointment_type=appointment_type,
            start_time_iso=start_time_str,
            target_date=target_date,
            db=db,
        )
    except ValueError as e:
        return f"Could not book appointment: {str(e)}"

    # Format start_time for user-friendly output
    formatted_time = appointment.start_time.strftime("%A, %b %d at %I:%M %p")
    return f"Appointment booked for {active_patient.full_name} on {formatted_time} ({appointment.appointment_type})."


@dental_agent.tool
async def get_available_slots(
    ctx: RunContext[DentalDependencies], target_date: date
) -> str:
    """
    Fetch available appointment slots for the given target_date.

    Args:
        target_date: datetime.date object.

    Returns:
        A readable list of available appointment times.
    """
    db = ctx.deps.db

    # Fetch available slots
    appointment_slots = await list_available_slots_for_date(
        target_date=target_date,
        db=db,
    )

    if not appointment_slots:
        return f"Sorry, there are no available appointment slots on {target_date.strftime('%A, %b %d')}."

    # Format for user-friendly display
    slots_str = ", ".join([slot.strftime("%I:%M %p") for slot in appointment_slots])
    return f"Available appointment slots on {target_date.strftime('%A, %b %d')}: {slots_str}."


@dental_agent.tool
async def escalate_to_human(
    ctx: RunContext[DentalDependencies], reason: Optional[str] = None
) -> str:
    """Escalate the current conversation to a human admin."""
    if not ctx.deps.conversation_id:
        return "Could not find conversation ID for escalation."

    await escalate_conversation_to_admin(conversation_id=ctx.deps.conversation_id)
    return "I've escalated this chat to one of our human staff — they’ll be with you shortly."


# ─────────────────────────────────────────────
# Context-aware instructions
# ─────────────────────────────────────────────


@dental_agent.instructions
async def existing_appointment(ctx: RunContext[DentalDependencies]) -> str:
    """
    Add context about the current patient's upcoming or existing appointments.
    This helps the agent respond naturally about scheduling, conflicts, or reminders.
    """
    db = ctx.deps.db
    active_conversation = await db.get(Conversation, ctx.deps.conversation_id)
    active_patient = await db.get(Patient, active_conversation.patient_id)

    if not active_patient:
        return "No patient identified yet. Ask for the phone number first."

    appointments = await list_appointments_for_patient(
        active_conversation.patient_id, db=db
    )

    if not appointments:
        return f"Patient {active_patient.full_name} has no scheduled appointments."

    # Build a summary of upcoming appointments
    upcoming = [
        appt
        for appt in appointments
        if appt.status == "scheduled" and appt.start_time >= datetime.now()
    ]
    if not upcoming:
        return f"Patient {active_patient.full_name} has no upcoming appointments."

    appointment_summaries = []
    for appt in upcoming:
        formatted_time = appt.start_time.strftime("%A, %b %d at %I:%M %p")
        appointment_summaries.append(f"- {appt.appointment_type} on {formatted_time}")

    summary_text = "\n".join(appointment_summaries)
    return f"Patient {active_patient.full_name} has the following upcoming appointments:\n{summary_text}"


@dental_agent.instructions
async def enrich_context(ctx: RunContext[DentalDependencies]) -> str:
    """Inject patient details into context if available."""
    db = ctx.deps.db
    active_conversation = await db.get(Conversation, ctx.deps.conversation_id)
    active_patient = await db.get(Patient, active_conversation.patient_id)
    if active_patient:
        return f"The current patient is {active_patient.full_name}, born {active_patient.date_of_birth}, phone {active_patient.phone_number}, insurance: {active_patient.insurance_name or 'none'}."
    return "No patient identified yet. Ask for phone number first."


@dental_agent.instructions
async def conversation_history(ctx: RunContext[str]) -> str:
    chat_message = await get_messages(conversation_id=ctx.deps.conversation_id)

    if len(chat_message) > 0:
        return f"Here is a list of previously exchange messages {
            [
                {
                    'role': 'user'
                    if m.sender_type == SenderTypeEnum.PATIENT.value
                    else 'model',
                    'timestamp': m.created_at,
                    'content': m.content,
                }
                for m in chat_message
            ]
        }"

    else:
        return "No conversational history"


async def handle_user_message(conversation_id, message):
    async for db in get_db():
        deps = DentalDependencies(db=db, conversation_id=conversation_id)
        result = await dental_agent.run(message, deps=deps)
        print("============ agent result ============ ", result)
        return result.output.message
