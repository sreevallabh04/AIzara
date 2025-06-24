"""
Test suite for Zara's memory system.
Tests database operations, backup functionality, and error handling.
"""

import pytest
import sqlite3
from pathlib import Path
import json
import shutil
from datetime import datetime

from zara.memory import get_memory_manager, MemoryManager

@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test_zara.db"

@pytest.fixture
def test_memory(monkeypatch, test_db_path):
    """Create a test memory instance with temporary database."""
    # Mock the database path
    def mock_init(self):
        self.db_path = test_db_path
        self.backup_dir = test_db_path.parent / "backups"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        with self._get_db() as (conn, _):
            self._setup_tables(conn)
    
    monkeypatch.setattr(MemoryManager, "_initialize", mock_init)
    return get_memory_manager()

def test_memory_singleton():
    """Test that memory manager is a singleton."""
    mem1 = get_memory_manager()
    mem2 = get_memory_manager()
    assert mem1 is mem2

def test_table_creation(test_memory, test_db_path):
    """Test that all required tables are created."""
    with sqlite3.connect(test_db_path) as conn:
        cursor = conn.cursor()
        # Check tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (
                'chat_history', 'tasks', 'user_preferences', 'semantic_memory'
            )
        """)
        tables = {row[0] for row in cursor.fetchall()}
        assert tables == {'chat_history', 'tasks', 'user_preferences', 'semantic_memory'}

def test_chat_storage(test_memory):
    """Test storing and retrieving chat messages."""
    # Store test messages
    test_memory.store_chat("user", "Hello Zara!")
    test_memory.store_chat("assistant", "Hello! How can I help?")
    
    # Retrieve messages
    messages = test_memory.get_recent_chat(limit=2)
    assert len(messages) == 2
    assert messages[0]['speaker'] == 'assistant'
    assert messages[0]['content'] == 'Hello! How can I help?'
    assert messages[1]['speaker'] == 'user'
    assert messages[1]['content'] == 'Hello Zara!'

def test_task_management(test_memory):
    """Test task creation and status updates."""
    # Create task
    test_memory.store_task("Test task", {"priority": "high"})
    
    # Get pending tasks
    tasks = test_memory.get_pending_tasks()
    assert len(tasks) == 1
    assert tasks[0]['description'] == 'Test task'
    assert tasks[0]['status'] == 'pending'
    
    # Update task status
    test_memory.update_task_status(tasks[0]['id'], 'completed')
    pending = test_memory.get_pending_tasks()
    assert len(pending) == 0

def test_preferences(test_memory):
    """Test user preference storage and retrieval."""
    # Store preferences
    test_memory.set_preference('theme', 'dark')
    test_memory.set_preference('volume', 0.8)
    
    # Retrieve preferences
    assert test_memory.get_preference('theme') == 'dark'
    assert test_memory.get_preference('volume') == 0.8
    assert test_memory.get_preference('nonexistent', 'default') == 'default'

def test_semantic_memory(test_memory):
    """Test semantic memory storage and retrieval."""
    # Store concept
    test_memory.store_semantic_memory(
        "python",
        "Python is a high-level programming language",
        confidence=0.95
    )
    
    # Retrieve concept
    memory = test_memory.get_semantic_memory("python")
    assert memory is not None
    assert memory['concept'] == 'python'
    assert memory['confidence'] == 0.95

def test_error_handling(test_memory):
    """Test error handling for invalid operations."""
    with pytest.raises(sqlite3.Error):
        # Try to store invalid data
        test_memory.store_chat(None, None)

def test_context_handling(test_memory):
    """Test storing and retrieving messages with context."""
    context = {
        "timestamp": "2024-01-01T12:00:00",
        "location": "home",
        "mood": "happy"
    }
    
    # Store with context
    test_memory.store_chat("user", "Hi!", context)
    
    # Retrieve and verify
    messages = test_memory.get_recent_chat(limit=1)
    stored_context = json.loads(messages[0]['context'])
    assert stored_context['location'] == 'home'
    assert stored_context['mood'] == 'happy'

def test_backup_creation(test_memory, test_db_path):
    """Test database backup functionality."""
    # Add some data
    test_memory.store_chat("user", "Test message")
    
    # Trigger backup
    test_memory._schedule_backup()
    
    # Check backup exists
    backup_files = list(test_db_path.parent.glob("backups/zara_backup_*.db"))
    assert len(backup_files) > 0

def test_backup_rotation(test_memory, test_db_path):
    """Test that only last 5 backups are kept."""
    # Create multiple backups
    for i in range(7):
        test_memory._schedule_backup()
    
    # Check only 5 backups exist
    backup_files = list(test_db_path.parent.glob("backups/zara_backup_*.db"))
    assert len(backup_files) == 5

def test_database_recovery(test_memory, test_db_path):
    """Test database recovery from backup."""
    # Store initial data
    test_memory.store_chat("user", "Important message")
    test_memory._schedule_backup()
    
    # Simulate database corruption
    test_db_path.unlink()
    
    # Get new memory manager instance (should recover from backup)
    recovered_memory = get_memory_manager()
    messages = recovered_memory.get_recent_chat(limit=1)
    
    assert len(messages) == 1
    assert messages[0]['content'] == "Important message"