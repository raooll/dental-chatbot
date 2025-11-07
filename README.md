🦷 Dental Chatbot Backend

A modular FastAPI + SQLAlchemy (async) backend for managing patient information and appointment bookings.
Built using a DDD-inspired folder structure and managed entirely with uv for dependency management, environment setup, and command execution.

🧩 Project Structure

app/
├── db/
│ ├── database.py # Async engine + get_db()
│ └── alembic/ # Alembic migrations
├── patient_info/
│ ├── models.py # SQLAlchemy model for Patient
│ ├── interface.py # CRUD operations for Patient
│ └── fixtures.py # CLI fixture to seed fake patients
├── appointment/
│ ├── models.py # SQLAlchemy model for Appointment
│ ├── interface.py # CRUD operations for Appointment
│ └── fixtures.py # CLI fixture to seed fake Appointment
├── main.py # FastAPI entrypoint
└── pyproject.toml # Project configuration (used by uv)

🚀 Quick Start
1️⃣ Clone the repository

cd dental-chatbot

2️⃣ Install dependencies with uv

uv handles environment management and dependency installation automatically:

uv sync

To run any command inside the project environment, always prefix it with uv run.

3️⃣ Database setup

The project uses SQLite by default (app/db/app.db).

Run initial migrations:

uv run alembic upgrade head


4️⃣ Seed sample data (fixtures)

You can populate the database with fake test data using the included fixtures.

Create fake patients

 uv run python -m app.patient_info.fixtures --count 25

Create fake appointments

uv run python -m app.appointments.fixtures --count 25

Create fake conversations

uv run python -m app.conversations.fixtures --count 25

5️⃣ Run the FastAPI server

uv run fastapi dev app/main.py

By default, the server runs at:
http://127.0.0.1:8000

Development Notes

Use uv for everything (no pip, no venv).

Alembic migrations are stored in app/db/alembic/versions.

All CRUD logic is async and lives under interface.py in each domain.

Fixtures use Faker to generate realistic test data.

DDD structure ensures each domain (patient, appointment, etc.) is self-contained.

Useful Commands

Generate a new Alembic migration:
uv run alembic revision --autogenerate -m "your message"

Apply migrations:
uv run alembic upgrade head

Rollback one migration:
uv run alembic downgrade -1

Run tests (if configured):
uv run pytest


### Architecture & DDD Approach

This project is structured following Domain-Driven Design (DDD) principles, separating the codebase into clear domain boundaries, each responsible for a specific area of the system. This helps maintain modularity, scalability, and testability as the application grows.

Key Domains

Patient Info

Manages all patient-related data and operations.

Core entities: Patient.

Repositories and interfaces handle CRUD operations, patient lookup, and registration.

Appointments

Responsible for booking, rescheduling, and cancelling appointments.

Core entities: Appointment, AppointmentType, AppointmentStatus.

Provides logic for available slots, business hours validation, and conflict detection.

Conversations

Handles chat sessions between patients and the AI assistant.

Core entities: Conversation, Message.

Maintains conversation state, metadata, and history for context-aware interactions.

Supports escalation to human staff when required.

AI Agent

Encapsulates the intelligent dental assistant using a language model (e.g., Gemini 2.5).

Tools correspond to domain actions like find_patient, register_patient, book_appointment, get_available_slots, and escalate_to_human.

Instructions are context-aware and maintain a friendly, human-like tone in responses.

### Directory structure

app/
├─ appointments/          # Appointment domain (entities, interface, business logic)
├─ patient_info/          # Patient domain (entities, interface, registration)
├─ conversations/         # Conversation domain (entities, interface, websocket events, agent)
├─ db/                    # Database connection and utilities
├─ websocket_app.py  


### TODO / Roadmap

The following enhancements and features are planned to improve the Dental Chatbot system:

#### Error Handling & Resilience

Handle and report agent errors gracefully.

Validate user inputs to prevent model or database errors.

Ensure conversation metadata (conversation.meta) remains consistent even on failures.

Add retry logic for database and external service calls.

####  User Experience Improvements

Provide real-time UI updates for pending operations (e.g., booking, slot checking).

Improve error messages to users with actionable suggestions.

Make agent responses more natural and context-aware.

Make cancel & reschedule flow work.

####  Admin Dashboard & Escalation

Build an admin chat page to monitor escalated messages in real-time.

Implement message routing logic to assign escalated conversations to available staff.

Log all escalations with timestamps and reason codes for audit purposes.

Allow admins to respond directly to patients through the dashboard.

####  Testing & QA

Add unit tests for domain services, repositories, and agent tools.

Implement integration tests for the WebSocket chat flow.

Validate end-to-end conversation scenarios (patient registration → booking → escalation).

Ensure edge cases (conflicting appointments, invalid inputs) are fully tested.
