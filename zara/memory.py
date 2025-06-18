"""
Memory management system for Zara Assistant.
Handles persistent storage, retrieval, and backup of various memory types.
"""

import sqlite3
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import numpy as np
from dataclasses import dataclass
from contextlib import contextmanager
import threading
from .logger import get_logger

logger = get_logger()

@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    content: str
    timestamp: datetime
    memory_type: str
    context: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

class MemoryManager:
    """Manages Zara's memory system with automatic backups and error handling."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the memory system."""
        self.db_path = Path('data/zara_assistant.db')
        self.backup_dir = Path('data/backups')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        with self._get_db() as (conn, _):
            self._setup_tables(conn)
        
        # Schedule first backup
        self._schedule_backup()
    
    @contextmanager
    def _get_db(self):
        """Context manager for database connections with error handling."""
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            yield conn, cursor
        except sqlite3.Error as e:
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def _setup_tables(self, conn: sqlite3.Connection):
        """Set up database tables with proper indexes."""
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    speaker TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    context TEXT
                );
                
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    context TEXT
                );
                
                CREATE TABLE IF NOT EXISTS user_preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS semantic_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT NOT NULL,
                    knowledge TEXT NOT NULL,
                    confidence FLOAT,
                    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_history(timestamp);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_semantic_concept ON semantic_memory(concept);
            """)
            conn.commit()
            logger.info("Database tables initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to setup database tables: {str(e)}")
            raise
    
    def _schedule_backup(self):
        """Schedule the next database backup."""
        try:
            now = datetime.now()
            backup_path = self.backup_dir / f"zara_backup_{now.strftime('%Y%m%d_%H%M%S')}.db"
            
            with self._get_db() as (conn, _):
                shutil.copy2(self.db_path, backup_path)
            
            # Keep only last 5 backups
            backups = sorted(self.backup_dir.glob("zara_backup_*.db"))
            if len(backups) > 5:
                for old_backup in backups[:-5]:
                    old_backup.unlink()
            
            logger.info(f"Database backup created: {backup_path.name}")
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
    
    def store_chat(self, speaker: str, content: str, context: Optional[Dict] = None):
        """Store a chat interaction."""
        try:
            with self._get_db() as (conn, cursor):
                cursor.execute(
                    "INSERT INTO chat_history (speaker, content, context) VALUES (?, ?, ?)",
                    (speaker, content, json.dumps(context) if context else None)
                )
                conn.commit()
            logger.info(f"Stored chat message from {speaker}")
        except sqlite3.Error as e:
            logger.error(f"Failed to store chat: {str(e)}")
            raise
    
    def get_recent_chat(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent chat history."""
        try:
            with self._get_db() as (_, cursor):
                cursor.execute(
                    "SELECT * FROM chat_history ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve chat history: {str(e)}")
            return []
    
    def store_task(self, description: str, context: Optional[Dict] = None):
        """Store a new task."""
        try:
            with self._get_db() as (conn, cursor):
                cursor.execute(
                    "INSERT INTO tasks (description, status, context) VALUES (?, ?, ?)",
                    (description, "pending", json.dumps(context) if context else None)
                )
                conn.commit()
            logger.info(f"Stored new task: {description[:50]}...")
        except sqlite3.Error as e:
            logger.error(f"Failed to store task: {str(e)}")
            raise
    
    def update_task_status(self, task_id: int, status: str):
        """Update task status."""
        try:
            with self._get_db() as (conn, cursor):
                cursor.execute(
                    """UPDATE tasks 
                       SET status = ?, 
                           completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END 
                       WHERE id = ?""",
                    (status, status, task_id)
                )
                conn.commit()
            logger.info(f"Updated task {task_id} status to {status}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update task status: {str(e)}")
            raise
    
    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks."""
        try:
            with self._get_db() as (_, cursor):
                cursor.execute("SELECT * FROM tasks WHERE status = 'pending'")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve pending tasks: {str(e)}")
            return []
    
    def set_preference(self, key: str, value: Union[str, int, float, bool, dict]):
        """Store a user preference."""
        try:
            with self._get_db() as (conn, cursor):
                cursor.execute(
                    """INSERT INTO user_preferences (key, value) 
                       VALUES (?, ?) 
                       ON CONFLICT(key) DO UPDATE SET 
                           value = excluded.value,
                           updated_at = CURRENT_TIMESTAMP""",
                    (key, json.dumps(value))
                )
                conn.commit()
            logger.info(f"Updated preference: {key}")
        except sqlite3.Error as e:
            logger.error(f"Failed to set preference: {str(e)}")
            raise
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Retrieve a user preference."""
        try:
            with self._get_db() as (_, cursor):
                cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
                row = cursor.fetchone()
                return json.loads(row['value']) if row else default
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve preference: {str(e)}")
            return default
    
    def store_semantic_memory(self, concept: str, knowledge: str, confidence: float = 1.0):
        """Store semantic knowledge."""
        try:
            with self._get_db() as (conn, cursor):
                cursor.execute(
                    """INSERT INTO semantic_memory (concept, knowledge, confidence) 
                       VALUES (?, ?, ?)""",
                    (concept, knowledge, confidence)
                )
                conn.commit()
            logger.info(f"Stored semantic memory: {concept}")
        except sqlite3.Error as e:
            logger.error(f"Failed to store semantic memory: {str(e)}")
            raise
    
    def get_semantic_memory(self, concept: str) -> Optional[Dict]:
        """Retrieve semantic knowledge."""
        try:
            with self._get_db() as (conn, cursor):
                cursor.execute(
                    """SELECT * FROM semantic_memory 
                       WHERE concept = ? 
                       ORDER BY confidence DESC LIMIT 1""",
                    (concept,)
                )
                row = cursor.fetchone()
                if row:
                    # Update last accessed timestamp
                    cursor.execute(
                        "UPDATE semantic_memory SET last_accessed = CURRENT_TIMESTAMP WHERE id = ?",
                        (row['id'],)
                    )
                    conn.commit()
                    return dict(row)
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve semantic memory: {str(e)}")
            return None

# Convenience function to get the memory manager instance
def get_memory_manager() -> MemoryManager:
    """Get the singleton memory manager instance."""
    return MemoryManager()