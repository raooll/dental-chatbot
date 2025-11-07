from app.conversations import interface as converstaion_interface
from app.websocket_app import sio


@sio.event(namespace="/conversations")
async def connect(sid, environ):
    print("Connected to /conversations:", sid)


@sio.event(namespace="/conversations")
async def disconnect(sid):
    print("Disconnected from /conversations:", sid)


@sio.event(namespace="/conversations")
async def start_conversation(sid, data):
    content = data["content"]

    conversation_id, ai_message = await converstaion_interface.process_user_message(
        conversation_id=None, content=content
    )

    await sio.emit(
        "conversation_started",
        {"conversation_id": str(conversation_id)},
        to=sid,
        namespace="/conversations",
    )

    await sio.enter_room(sid, str(conversation_id), namespace="/conversations")

    await sio.emit(
        "new_message",
        {"conversation_id": str(conversation_id), "content": ai_message},
        room=str(conversation_id),
        namespace="/conversations",
    )


@sio.event(namespace="/conversations")
async def send_message(sid, data):
    conversation_id = data.get("conversation_id")
    content = data["content"]

    conversation_id, ai_message = await converstaion_interface.process_user_message(
        conversation_id=conversation_id, content=content
    )

    await sio.emit(
        "new_message",
        {"conversation_id": str(conversation_id), "content": ai_message},
        room=str(conversation_id),
        namespace="/conversations",
    )
