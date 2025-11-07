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

This will apply:

81fd9ea8222a → Creates the patients table

3d76e3776eb0 → Creates the appointments table

4️⃣ Seed sample data (fixtures)

You can populate the database with fake test data using the included fixtures.

🧍 Create fake patients

 uv run python -m app.patient_info.fixtures --count 25

📅 Create fake appointments

uv run python -m app.appointment.fixtures --count 25

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