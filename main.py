from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from database import init_db, insert_message, get_all_messages, get_db, get_connection
from datetime import datetime
import sqlite3
import os
import uvicorn

app = FastAPI()
app.mount('/static', StaticFiles(directory = 'static'), name = 'static')

init_db()  # <-- runs ONCE when server starts


class Message(BaseModel):
    email: str
    content: str


@app.post("/post_message")
async def post_message(message: Message):
    with get_connection() as db:
        if not can_send_message(message.email, db):
            return {"error": "Daily message limit reached!"}, 403  # reject if over limit

        timestamp = datetime.utcnow().isoformat()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO messages (email, content, timestamp) VALUES (?, ?, ?)",
            (message.email, message.content, timestamp)
        )
        db.commit()
    return {"success": True}


@app.get('/')
def get_home():
    with open('index.html') as f:
        return HTMLResponse(f.read())


@app.get("/messages")
def get_messages():
    rows = get_all_messages()
    return [
        {
            "email": r[0],
            "content": r[1],
            "timestamp": r[2]
        }
        for r in rows
    ]

MAX_MESSAGES_PER_DAY = 2

def can_send_message(email: str, db_connection):
    """check if the user has messages left for today."""
    today = datetime.utcnow().date()
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM messages
        WHERE email = ? AND DATE(timestamp) = ?
    """, (email, today))

    count = cursor.fetchone()[0]
    return count < MAX_MESSAGES_PER_DAY

@app.get("/messages/count")
async def messages_count(email:str):
    with get_connection() as db:
        today = datetime.utcnow().date()
        cursor = db.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM messages
            WHERE email = ? AND DATE(timestamp) = ?
        """, (email, today))
        count = cursor.fetchone()[0]
        return {"count": count}
    

port = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=port)