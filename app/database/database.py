import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict
import json

class SessionDatabase:
    def __init__(self, db_path: str = "app/database/sessions.db"):
        self.db_path = db_path
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
        self.migrate_db()
    
    def init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_id INTEGER,
                    username TEXT,
                    document_name TEXT,
                    document_type TEXT,
                    document_path TEXT,
                    document_url TEXT,
                    pinecone_index TEXT,
                    pinecone_namespace TEXT,
                    chunks_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            conn.commit()
    
    def migrate_db(self):
        """Handle database migrations for existing databases"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if document_name column exists in sessions table
            cursor.execute("PRAGMA table_info(sessions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'document_name' not in columns:
                print("[Database] Adding document_name column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN document_name TEXT")
                conn.commit()
                print("[Database] Migration completed: document_name column added")
            
            # Check if document_type column exists
            if 'document_type' not in columns:
                print("[Database] Adding document_type column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN document_type TEXT")
                conn.commit()
                print("[Database] Migration completed: document_type column added")
            
            # Check if document_path column exists
            if 'document_path' not in columns:
                print("[Database] Adding document_path column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN document_path TEXT")
                conn.commit()
                print("[Database] Migration completed: document_path column added")
            
            # Check if document_url column exists
            if 'document_url' not in columns:
                print("[Database] Adding document_url column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN document_url TEXT")
                conn.commit()
                print("[Database] Migration completed: document_url column added")
            
            # Check if pinecone_index column exists
            if 'pinecone_index' not in columns:
                print("[Database] Adding pinecone_index column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN pinecone_index TEXT")
                conn.commit()
                print("[Database] Migration completed: pinecone_index column added")
            
            # Check if pinecone_namespace column exists
            if 'pinecone_namespace' not in columns:
                print("[Database] Adding pinecone_namespace column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN pinecone_namespace TEXT")
                conn.commit()
                print("[Database] Migration completed: pinecone_namespace column added")
            
            # Check if chunks_count column exists
            if 'chunks_count' not in columns:
                print("[Database] Adding chunks_count column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN chunks_count INTEGER DEFAULT 0")
                conn.commit()
                print("[Database] Migration completed: chunks_count column added")
            
            # Check if is_active column exists
            if 'is_active' not in columns:
                print("[Database] Adding is_active column to sessions table...")
                cursor.execute("ALTER TABLE sessions ADD COLUMN is_active BOOLEAN DEFAULT 1")
                conn.commit()
                print("[Database] Migration completed: is_active column added")
    
    def create_user(self, username: str, email: str = None) -> int:
        """Create a new user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO users (username, email) VALUES (?, ?)",
                    (username, email)
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # User already exists, return existing user_id
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                result = cursor.fetchone()
                return result[0] if result else None
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, email, created_at FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'email': result[2],
                    'created_at': result[3]
                }
            return None
    
    def create_session(self, session_id: str, username: str, 
                      document_name: str = None, document_type: str = None,
                      document_path: str = None, document_url: str = None) -> bool:
        """Create a new session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user_id
            user = self.get_user(username)
            if not user:
                user_id = self.create_user(username)
            else:
                user_id = user['id']
            
            cursor.execute("""
                INSERT INTO sessions 
                (session_id, user_id, username, document_name, document_type, 
                 document_path, document_url, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, user_id, username, document_name, document_type,
                  document_path, document_url, datetime.now()))
            
            conn.commit()
            return True
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session with new information"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['pinecone_index', 'pinecone_namespace', 'chunks_count', 
                          'document_name', 'document_type', 'document_path', 'document_url']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if update_fields:
                update_fields.append("last_accessed = ?")
                values.append(datetime.now())
                values.append(session_id)
                
                query = f"UPDATE sessions SET {', '.join(update_fields)} WHERE session_id = ?"
                cursor.execute(query, values)
                conn.commit()
                return cursor.rowcount > 0
            
            return False
    
    def get_user_sessions(self, username: str) -> List[Dict]:
        """Get all sessions for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, document_name, document_type, chunks_count,
                       created_at, last_accessed, is_active, pinecone_index, pinecone_namespace
                FROM sessions 
                WHERE username = ? AND is_active = 1
                ORDER BY last_accessed DESC
            """, (username,))
            
            results = cursor.fetchall()
            return [
                {
                    'session_id': row[0],
                    'document_name': row[1],
                    'document_type': row[2],
                    'chunks_count': row[3],
                    'created_at': row[4],
                    'last_accessed': row[5],
                    'is_active': row[6],
                    'pinecone_index': row[7],
                    'pinecone_namespace': row[8]
                }
                for row in results
            ]
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by session_id"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT session_id, username, document_name, document_type, 
                       document_path, document_url, pinecone_index, pinecone_namespace,
                       chunks_count, created_at, last_accessed, is_active
                FROM sessions 
                WHERE session_id = ?
            """, (session_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'session_id': result[0],
                    'username': result[1],
                    'document_name': result[2],
                    'document_type': result[3],
                    'document_path': result[4],
                    'document_url': result[5],
                    'pinecone_index': result[6],
                    'pinecone_namespace': result[7],
                    'chunks_count': result[8],
                    'created_at': result[9],
                    'last_accessed': result[10],
                    'is_active': result[11]
                }
            return None
    
    def add_chat_message(self, session_id: str, question: str, answer: str) -> bool:
        """Add a chat message to history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (session_id, question, answer)
                VALUES (?, ?, ?)
            """, (session_id, question, answer))
            conn.commit()
            return True
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT question, answer, timestamp
                FROM chat_history 
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """, (session_id,))
            
            results = cursor.fetchall()
            return [
                {
                    'question': row[0],
                    'answer': row[1],
                    'timestamp': row[2]
                }
                for row in results
            ]
    
    def deactivate_session(self, session_id: str) -> bool:
        """Deactivate a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE sessions SET is_active = 0 WHERE session_id = ?
            """, (session_id,))
            conn.commit()
            return cursor.rowcount > 0
