from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pathlib
from app.websocket_app import socket_app


import logging
logging.getLogger("engineio").setLevel(logging.DEBUG)
logging.getLogger("socketio").setLevel(logging.DEBUG)


import app.conversations


app = FastAPI(title="Dental Chatbot")

app.mount("/ws", socket_app)

# Serve static files (chat.html, chat.js)
static_dir = pathlib.Path(__file__).parent / "app" / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Enable CORS (optional for local testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def home():
    html_file = static_dir  / "chat.html"
    return HTMLResponse(content=html_file.read_text(), status_code=200)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    
    # For now, simple echo logic
    return JSONResponse({"message": f"You said: {message}"})
