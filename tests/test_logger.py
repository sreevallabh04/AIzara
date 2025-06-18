"""
Test suite for Zara's logging system.
Tests log file creation, rotation, and various logging functionalities.
"""

import pytest
import logging
import sys
from pathlib import Path
import time
import json
from unittest.mock import patch, MagicMock
import io

from zara.logger import get_logger, ZaraLogger

@pytest.fixture
def temp_log_dir(tmp_path):
    """Create a temporary directory for log files."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir

@pytest.fixture
def test_logger(monkeypatch, temp_log_dir):
    """Create a test logger instance with temporary directory."""
    # Reset singleton
    ZaraLogger._instance = None
    
    def mock_initialize(self):
        self.logger = logging.getLogger('zara_test')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            temp_log_dir / 'zara.log',
            maxBytes=500,  # Small size for testing rotation
            backupCount=3
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        sys.excepthook = self._global_exception_handler
    
    monkeypatch.setattr(ZaraLogger, "_initialize", mock_initialize)
    return get_logger()

def test_logger_singleton():
    """Test that logger is a singleton."""
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2

def test_log_file_creation(test_logger, temp_log_dir):
    """Test log file is created and written to."""
    test_logger.info("Test message")
    log_file = temp_log_dir / "zara.log"
    assert log_file.exists()
    content = log_file.read_text()
    assert "Test message" in content

def test_log_rotation(test_logger, temp_log_dir):
    """Test log file rotation."""
    # Write enough data to trigger rotation
    for i in range(100):
        test_logger.info("X" * 100)
    
    # Check rotation files exist
    log_files = list(temp_log_dir.glob("zara.log*"))
    assert len(log_files) > 1
    assert len(log_files) <= 4  # Original + 3 backups

def test_log_levels(test_logger):
    """Test different log levels."""
    with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        test_logger.critical("Critical message")
        
        output = fake_stdout.getvalue()
        # Debug shouldn't be present as level is INFO
        assert "Debug message" not in output
        assert "Info message" in output
        assert "Warning message" in output
        assert "Error message" in output
        assert "Critical message" in output

def test_exception_handling(test_logger):
    """Test exception logging."""
    with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
        try:
            raise ValueError("Test error")
        except Exception as e:
            test_logger.error("Error occurred", exc_info=True)
        
        output = fake_stdout.getvalue()
        assert "ValueError: Test error" in output
        assert "Traceback" in output

def test_user_interaction_logging():
    """Test logging of user interactions."""
    logger = get_logger()
    with patch.object(logger, 'info') as mock_info:
        ZaraLogger.log_user_interaction(
            "Hello Zara",
            "Hello! How can I help?"
        )
        
        assert mock_info.call_count == 2
        calls = [call[0][0] for call in mock_info.call_args_list]
        assert any("User" in call for call in calls)
        assert any("Zara" in call for call in calls)

def test_tool_call_logging():
    """Test logging of tool executions."""
    logger = get_logger()
    with patch.object(logger, 'info') as mock_info:
        ZaraLogger.log_tool_call(
            "vision_system",
            "success",
            "Processed image successfully"
        )
        
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        assert "vision_system" in call_args
        assert "success" in call_args

def test_error_logging():
    """Test error logging functionality."""
    logger = get_logger()
    with patch.object(logger, 'error') as mock_error:
        ZaraLogger.log_error(
            "API_ERROR",
            "Failed to connect",
            "Connection timeout"
        )
        
        mock_error.assert_called_once()
        call_args = mock_error.call_args[0][0]
        assert "API_ERROR" in call_args
        assert "Failed to connect" in call_args

def test_global_exception_handler(test_logger):
    """Test global exception handler."""
    with patch('sys.stdout', new=io.StringIO()):
        with patch.object(test_logger, 'critical') as mock_critical:
            # Simulate uncaught exception
            sys.excepthook(ValueError, ValueError("Test error"), None)
            
            mock_critical.assert_called_once()
            assert "Uncaught exception" in mock_critical.call_args[0][0]

def test_log_format(test_logger, temp_log_dir):
    """Test log message formatting."""
    test_logger.info("Test format")
    log_content = (temp_log_dir / "zara.log").read_text()
    
    # Check format components
    assert " - INFO - " in log_content
    assert "test_logger - " in log_content
    assert "Test format" in log_content

def test_concurrent_logging(test_logger):
    """Test logging from multiple threads."""
    import threading
    
    def log_messages():
        for i in range(10):
            test_logger.info(f"Thread message {i}")
    
    threads = [
        threading.Thread(target=log_messages)
        for _ in range(3)
    ]
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # No assertions needed - just checking it doesn't raise exceptions

def test_logger_cleanup(test_logger):
    """Test logger cleanup and handler removal."""
    original_handlers = len(test_logger.handlers)
    
    # Reset singleton
    ZaraLogger._instance = None
    new_logger = get_logger()
    
    # Should have same number of handlers (not duplicated)
    assert len(new_logger.handlers) == original_handlers