import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Use relative URLs so nginx can proxy to backend
const API_URL = process.env.REACT_APP_API_URL || '';

function App() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/notes`);
      setNotes(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching notes:', error);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    try {
      if (editingId) {
        await axios.put(`${API_URL}/api/notes/${editingId}`, {
          title,
          content,
        });
      } else {
        await axios.post(`${API_URL}/api/notes`, {
          title,
          content,
        });
      }
      setTitle('');
      setContent('');
      setEditingId(null);
      fetchNotes();
    } catch (error) {
      console.error('Error saving note:', error);
    }
  };

  const handleEdit = (note) => {
    setTitle(note.title);
    setContent(note.content);
    setEditingId(note.id);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await axios.delete(`${API_URL}/api/notes/${id}`);
        fetchNotes();
      } catch (error) {
        console.error('Error deleting note:', error);
      }
    }
  };

  const handleCancel = () => {
    setTitle('');
    setContent('');
    setEditingId(null);
  };

  if (loading) {
    return (
      <div className="app">
        <div className="container">
          <div className="loading">Loading notes...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="container">
        <h1 className="title">📝 Notes App</h1>
        <p className="subtitle">Docker Compose Practice</p>

        <form className="note-form" onSubmit={handleSubmit}>
          <input
            type="text"
            className="input"
            placeholder="Note Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <textarea
            className="textarea"
            placeholder="Note Content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows="4"
          />
          <div className="form-actions">
            <button type="submit" className="btn btn-primary">
              {editingId ? 'Update Note' : 'Add Note'}
            </button>
            {editingId && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleCancel}
              >
                Cancel
              </button>
            )}
          </div>
        </form>

        <div className="notes-grid">
          {notes.length === 0 ? (
            <div className="empty-state">No notes yet. Create your first note!</div>
          ) : (
            notes.map((note) => (
              <div key={note.id} className="note-card">
                <h3 className="note-title">{note.title}</h3>
                <p className="note-content">{note.content}</p>
                <div className="note-footer">
                  <span className="note-date">
                    {new Date(note.updated_at).toLocaleDateString()}
                  </span>
                  <div className="note-actions">
                    <button
                      className="btn-icon"
                      onClick={() => handleEdit(note)}
                      title="Edit"
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-icon"
                      onClick={() => handleDelete(note.id)}
                      title="Delete"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

