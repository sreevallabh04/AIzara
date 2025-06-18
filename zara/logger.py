"""
Central logging system for Zara Assistant.
Handles both console and file output with rotation.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

class ZaraLogger:
    _instance: Optional['ZaraLogger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Initialize the logger with both file and console handlers."""
        self.logger = logging.getLogger('zara')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'zara.log',
            maxBytes=5_000_000,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Set up global exception hook
        sys.excepthook = self._global_exception_handler
    
    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions globally."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Special handling for keyboard interrupt
            self.logger.info("Received keyboard interrupt, shutting down gracefully...")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        self.logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the singleton logger instance."""
        if cls._instance is None:
            cls()
        return cls._instance.logger
    
    @staticmethod
    def log_user_interaction(user_input: str, assistant_response: str):
        """Log user interactions with timestamps."""
        logger = ZaraLogger.get_logger()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"User [{timestamp}]: {user_input}")
        logger.info(f"Zara [{timestamp}]: {assistant_response}")
    
    @staticmethod
    def log_tool_call(tool_name: str, status: str, details: str = ""):
        """Log tool execution with status."""
        logger = ZaraLogger.get_logger()
        logger.info(f"Tool '{tool_name}' {status}: {details}")
    
    @staticmethod
    def log_error(error_type: str, error_msg: str, details: str = ""):
        """Log errors with type classification."""
        logger = ZaraLogger.get_logger()
        logger.error(f"{error_type}: {error_msg} - {details}")

# Create a convenience function to get the logger
def get_logger() -> logging.Logger:
    """Convenience function to get the Zara logger instance."""
    return ZaraLogger.get_logger()