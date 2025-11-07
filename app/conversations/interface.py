from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.conversations import appointment_agent
from app.conversations.models import (
    Conversation,
    Message,
    ConversationStatusEnum,
    SenderTypeEnum,
)
from app.db.utils import with_db
# ----------------------------
# Conversation CRUD
# ----------------------------


@with_db
async def create_conversation(db: AsyncSession = None) -> Conversation:
    conversation = Conversation(
        status=ConversationStatusEnum.ACTIVE.value,
        started_at=datetime.utcnow(),
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@with_db
async def get_conversation(
    conversation_id: str, db: AsyncSession = None
) -> Optional[Conversation]:
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    return result.scalars().first()


@with_db
async def update_conversation_status(
    conversation_id: str, status: str, db: AsyncSession = None
) -> Optional[Conversation]:
    conversation = await get_conversation(conversation_id, db=db)
    if not conversation:
        return None
    conversation.status = status
    if status == ConversationStatusEnum.ESCALATED.value:
        conversation.escalated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(conversation)
    return conversation


@with_db
async def escalate_conversation_to_admin(
    conversation_id: str, db: AsyncSession = None
) -> Optional[Conversation]:
    await update_conversation_status(
        conversation_id=conversation_id,
        status=ConversationStatusEnum.ESCALATED.value,
        db=db,
    )


@with_db
async def close_conversation(
    conversation_id: str, db: AsyncSession = None
) -> Optional[Conversation]:
    conversation = await get_conversation(conversation_id, db=db)
    if not conversation:
        return None
    conversation.status = ConversationStatusEnum.CLOSED.value
    conversation.closed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(conversation)
    return conversation


@with_db
async def list_conversations(
    patient_id: Optional[int] = None, db: AsyncSession = None
) -> List[Conversation]:
    query = select(Conversation)
    if patient_id is not None:
        query = query.where(Conversation.patient_id == patient_id)
    query = query.order_by(Conversation.started_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


# ----------------------------
# Message CRUD
# ----------------------------


@with_db
async def create_message(
    conversation_id: str,
    sender_type: str,
    content: str,
    patient_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    db: AsyncSession = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        sender_type=sender_type,
        content=content,
        meta=metadata,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@with_db
async def get_messages(conversation_id: str, db: AsyncSession = None) -> List[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


@with_db
async def get_message(message_id: str, db: AsyncSession = None) -> Optional[Message]:
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalars().first()


@with_db
async def delete_message(message_id: str, db: AsyncSession = None) -> bool:
    message = await get_message(message_id, db=db)
    if not message:
        return False
    await db.delete(message)
    await db.commit()
    return True


@with_db
async def update_message_content(
    message_id: str,
    content: str,
    metadata: Optional[dict] = None,
    db: AsyncSession = None,
) -> Optional[Message]:
    message = await get_message(message_id, db=db)
    if not message:
        return None
    message.content = content
    if metadata:
        message.metadata = metadata
    await db.commit()
    await db.refresh(message)
    return message


@with_db
async def process_user_message(
    conversation_id: int = None,
    content: str = None,
    db: AsyncSession = None,
):
    """
    Create conversation/message, send to agent, store response, and return AI reply.

    Args:
        conversation_id: existing conversation ID (if any)
        patient_id: patient ID (used if conversation needs creation)
        content: patient message text

    Returns:
        conversation_id, ai_message
    """
    # If no conversation exists, create one
    if not conversation_id:
        conversation = await create_conversation(db=db)
        conversation_id = conversation.id

    # Store patient's message
    msg = await create_message(
        conversation_id=conversation_id,
        sender_type=SenderTypeEnum.PATIENT,
        content=content,
        db=db,
    )

    # Get AI agent response
    ai_response = await appointment_agent.handle_user_message(
        conversation_id=conversation_id, message=msg.content
    )

    # Store AI response
    ai_msg = await create_message(
        conversation_id=conversation_id,
        sender_type=SenderTypeEnum.AI_AGENT,
        content=ai_response,
        db=db,
    )

    return conversation_id, ai_response
