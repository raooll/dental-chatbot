# websocket_app.py
import socketio

# Create global Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True,
)


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


# ASGI app (mountable in FastAPI)
socket_app = socketio.ASGIApp(sio, socketio_path="/ws/socket.io/")
