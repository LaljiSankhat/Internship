from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import os
from datetime import datetime

app = FastAPI(title="Notes API", version="1.0.0")

# CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "/app/data/notes.db"

def init_db():
    """Initialize the database and create notes table"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Pydantic models
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# API Routes
@app.get("/")
def read_root():
    return {"message": "Notes API is running!"}

@app.get("/api/notes", response_model=List[Note])
def get_notes():
    """Get all notes"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes ORDER BY updated_at DESC")
    notes = cursor.fetchall()
    conn.close()
    return [dict(note) for note in notes]

@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    """Get a specific note by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return dict(note)

@app.post("/api/notes", response_model=Note)
def create_note(note: NoteCreate):
    """Create a new note"""
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (note.title, note.content, now, now)
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    
    return get_note(note_id)

@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate):
    """Update an existing note"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get existing note
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update fields
    title = note.title if note.title is not None else existing["title"]
    content = note.content if note.content is not None else existing["content"]
    updated_at = datetime.now().isoformat()
    
    cursor.execute(
        "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
        (title, content, updated_at, note_id)
    )
    conn.commit()
    conn.close()
    
    return get_note(note_id)

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int):
    """Delete a note"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    conn.commit()
    conn.close()
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

