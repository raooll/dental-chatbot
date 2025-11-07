import asyncio
import random
from datetime import datetime, timedelta
import argparse

from sqlalchemy.future import select

from app.conversations.models import (
    Conversation,
    Message,
    ConversationStatusEnum,
    SenderTypeEnum,
)
from app.patient_info.models import Patient
from app.db.database import AsyncSessionLocal  # your AsyncSession factory


async def create_fixtures(conversation_count: int):
    async with AsyncSessionLocal() as db:  # assumes async_session() gives AsyncSession
        # 1. Load existing patients
        result = await db.execute(select(Patient))
        patients = result.scalars().all()

        # 2. Create conversations
        conversations = []
        for i in range(conversation_count):
            patient = (
                random.choice(patients) if patients and random.random() > 0.3 else None
            )
            conv = Conversation(
                patient_id=patient.id if patient else None,
                status=random.choice(
                    [
                        ConversationStatusEnum.ACTIVE.value,
                        ConversationStatusEnum.ESCALATED.value,
                    ]
                ),
                started_at=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
            )
            db.add(conv)
            conversations.append(conv)

        await db.commit()

        # 3. Create 3-7 messages per conversation
        sender_types = [
            SenderTypeEnum.PATIENT.value,
            SenderTypeEnum.AI_AGENT.value,
            SenderTypeEnum.HUMAN_AGENT.value,
        ]
        for conv in conversations:
            num_messages = random.randint(3, 7)
            for j in range(num_messages):
                sender_type = random.choice(sender_types)
                msg = Message(
                    conversation_id=conv.id,
                    sender_type=sender_type,
                    content=f"Sample message {j + 1} for conversation {conv.id}",
                )
                db.add(msg)

        await db.commit()
        print(f"Created {len(conversations)} conversations with sample messages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create sample conversations and messages"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of conversations to create (default: 5)",
    )
    args = parser.parse_args()

    asyncio.run(create_fixtures(args.count))
