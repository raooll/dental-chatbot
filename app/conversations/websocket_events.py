from app.conversations.interface import (
    create_conversation,
    create_message,
    get_messages,
)
from app.conversations.models import SenderTypeEnum
from app.db.database import AsyncSessionLocal
from app.conversations import appointment_agent
from app.websocket_app import sio


@sio.event(namespace="/conversations")
async def connect(sid, environ):
    print("Connected to /conversations:", sid)


@sio.event(namespace="/conversations")
async def disconnect(sid):
    print("Disconnected from /conversations:", sid)


@sio.event(namespace="/conversations")
async def start_conversation(sid, data):
    """
    Fired when a user sends the first message.
    data: {patient_id, content}
    """
    async with AsyncSessionLocal() as db:
        patient_id = data.get("patient_id")  # optional
        conversation = await create_conversation(patient_id=patient_id, db=db)

        await sio.emit(
            "conversation_started",
            {"conversation_id": str(conversation.id)},
            to=sid,
            namespace="/conversations",
        )

        # Put client in that room
        await sio.enter_room(sid, str(conversation.id), namespace="/conversations")

        msg = await create_message(
            conversation_id=conversation.id,
            sender_type=SenderTypeEnum.PATIENT,
            content=data["content"],
            db=db,
        )

        message = await appointment_agent.handle_user_message(
            conversation_id=conversation.id, message=msg.content
        )

        msg = await create_message(
            conversation_id=conversation.id,
            sender_type=SenderTypeEnum.AI_AGENT,
            content=message,
            db=db,
        )

        await sio.emit(
            "new_message",
            {
                "conversation_id": str(conversation.id),
                "content": msg.content,
            },
            room=str(conversation.id),
            namespace="/conversations",
        )


@sio.event(namespace="/conversations")
async def send_message(sid, data):
    async with AsyncSessionLocal() as db:
        conversation_id = data.get("conversation_id")
        print(dict(data))
        msg = await create_message(
            conversation_id=conversation_id,
            sender_type=SenderTypeEnum.PATIENT.value,
            content=data["content"],
            db=db,
        )

        message = await appointment_agent.handle_user_message(
            conversation_id=conversation_id, message=msg.content
        )

        msg = await create_message(
            conversation_id=conversation_id,
            sender_type=SenderTypeEnum.AI_AGENT,
            content=message,
            db=db,
        )

        await sio.emit(
            "new_message",
            {
                "conversation_id": str(conversation_id),
                "content": message,
            },
            room=str(conversation_id),
            namespace="/conversations",
        )


# # When a patient or admin joins a conversation
# @sio.event
# async def join(sid, data):
#     conversation_id = data.get("conversation_id")
#     if not conversation_id:
#         await sio.emit("error", {"message": "conversation_id required"}, to=sid)
#         return

#     await sio.save_session(sid, {"conversation_id": conversation_id})
#     await sio.enter_room(sid, conversation_id)
#     await sio.emit("joined", {"conversation_id": conversation_id}, room=sid)


# # When a user sends a message
# @sio.event
# async def send_message(sid, data):
#     conversation_id = data.get("conversation_id")
#     sender_type = data.get("sender_type", SenderTypeEnum.PATIENT.value)
#     content = data.get("content")

#     if not conversation_id or not content:
#         await sio.emit("error", {"message": "conversation_id and content required"}, to=sid)
#         return

#     async with AsyncSessionLocal() as db:
#         message = await create_message(
#             conversation_id=conversation_id,
#             sender_type=sender_type,
#             content=content,
#             db=db
#         )

#     # Broadcast message to everyone in this conversation room
#     await sio.emit("new_message", {
#         "conversation_id": conversation_id,
#         "sender_type": sender_type,
#         "content": content,
#         "timestamp": str(message.timestamp)
#     }, room=conversation_id)


# # Admin or AI agent escalation event
# @sio.event
# async def escalate_conversation(sid, data):
#     conversation_id = data.get("conversation_id")

#     async with AsyncSessionLocal() as db:
#         convo = await get_conversation(conversation_id, db=db)
#         if convo:
#             convo.status = "escalated"
#             await db.commit()
#             await sio.emit("conversation_escalated", {"conversation_id": conversation_id}, room=conversation_id)


# @sio.event
# async def disconnect(sid):
#     session = await sio.get_session(sid)
#     conversation_id = session.get("conversation_id") if session else None
#     if conversation_id:
#         await sio.leave_room(sid, conversation_id)
#     print(f"Client {sid} disconnected from {conversation_id}")
