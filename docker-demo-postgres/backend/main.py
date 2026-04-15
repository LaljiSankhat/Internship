from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import time

app = FastAPI(title="Notes API", version="1.0.0")

# CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "notesdb"),
    "user": os.getenv("DB_USER", "notesuser"),
    "password": os.getenv("DB_PASSWORD", "notespwd")
}

def get_db_connection():
    """Get a database connection"""
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    """Initialize the database and create notes table"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully!")
            return
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection failed. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts: {e}")
                raise

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
    return {"message": "Notes API is running with PostgreSQL!"}

@app.get("/api/notes", response_model=List[Note])
def get_notes():
    """Get all notes"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT id, title, content, created_at::text, updated_at::text FROM notes ORDER BY updated_at DESC")
    notes = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(note) for note in notes]

@app.get("/api/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    """Get a specific note by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, title, content, created_at::text, updated_at::text FROM notes WHERE id = %s",
        (note_id,)
    )
    note = cursor.fetchone()
    cursor.close()
    conn.close()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return dict(note)

@app.post("/api/notes", response_model=Note)
def create_note(note: NoteCreate):
    """Create a new note"""
    now = datetime.now()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content, created_at, updated_at) VALUES (%s, %s, %s, %s) RETURNING id",
        (note.title, note.content, now, now)
    )
    note_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    
    return get_note(note_id)

@app.put("/api/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate):
    """Update an existing note"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get existing note
    cursor.execute("SELECT * FROM notes WHERE id = %s", (note_id,))
    existing = cursor.fetchone()
    if existing is None:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update fields
    title = note.title if note.title is not None else existing["title"]
    content = note.content if note.content is not None else existing["content"]
    updated_at = datetime.now()
    
    cursor.execute(
        "UPDATE notes SET title = %s, content = %s, updated_at = %s WHERE id = %s",
        (title, content, updated_at, note_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    return get_note(note_id)

@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int):
    """Delete a note"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {"message": "Note deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
