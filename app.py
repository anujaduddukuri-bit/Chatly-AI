# app.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
import re

app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 templates for HTML rendering
templates = Jinja2Templates(directory="templates")


# -------------------------------
# Simple rule-based chatbot logic
# -------------------------------
def generate_reply(message: str) -> str:
    text = message.lower().strip()

    # greetings
    if re.search(r"\b(hi|hello|hey|hlo)\b", text):
        return "Hey! 👋 How can I help you today?"

    if "how are you" in text:
        return "I'm a bot — always ready! How about you?"

    if re.search(r"\b(weather|temperature|climate)\b", text):
        return "I can't fetch live weather yet, but I can soon — want me to add that feature?"

    if "joke" in text:
        return "Why do programmers prefer dark mode? Because light attracts bugs! 🐛"

    # small talk
    if "name" in text:
        return "I'm Chatly — your friendly real-time assistant."

    if text.endswith("?"):
        return "That's an interesting question — here's what I think: 🤔 (this is a demo reply)."

    # fallback
    return "Sorry, I didn't fully get that. Try rephrasing or ask for a 'joke' or 'weather'."


# -------------------------------
# HTTP route to serve the page
# -------------------------------
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------------------
# Manage connected clients
# -------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """Optional: send message to all connected clients"""
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))


manager = ConnectionManager()


# -------------------------------
# WebSocket endpoint
# -------------------------------
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Expect a JSON text with {'type': 'user_message', 'text': '...'}
            try:
                payload = json.loads(data)
                if payload.get("type") == "user_message":
                    user_text = payload.get("text", "")
                    # Simulate thinking latency
                    await asyncio.sleep(0.4)
                    bot_text = generate_reply(user_text)
                    # send back bot reply
                    bot_msg = {"type": "bot_message", "text": bot_text}
                    await manager.send_personal_message(bot_msg, websocket)
            except json.JSONDecodeError:
                # If non-json, treat as plain text
                bot_text = generate_reply(data)
                bot_msg = {"type": "bot_message", "text": bot_text}
                await manager.send_personal_message(bot_msg, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)