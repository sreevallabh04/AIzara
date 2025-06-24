"""
Main entry point for Zara Assistant when run as a module.
Handles initialization, first-run checks, and startup.
"""

import sys
import os
import subprocess
import sqlite3
from pathlib import Path
import requests
import time

from .logger import get_logger
from .memory import get_memory_manager
from .voice import get_voice_interface
from .agent import get_agent

logger = get_logger()

def check_ollama_server() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def check_llama_model() -> bool:
    """Check if LLaMA model is pulled."""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        models = response.json()
        return any(model['name'] == 'llama2' for model in models['models'])
    except Exception:
        return False

def ensure_database():
    """Ensure database exists and has required tables."""
    try:
        memory = get_memory_manager()
        logger.info("Database initialized successfully")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False

def speak_welcome():
    """Speak welcome message on first run."""
    try:
        voice = get_voice_interface()
        welcome_message = (
            "Hello! I'm Zara, your personal AI assistant. "
            "I'm now set up and ready to help you. "
            "You can ask me questions, give me tasks, or just chat. "
            "I'm particularly good at helping with your computer tasks "
            "and can see and understand images too!"
        )
        voice.speak(welcome_message)
        return True
    except Exception as e:
        logger.error(f"Failed to speak welcome message: {str(e)}")
        return False

def first_run_checks() -> bool:
    """Perform first-run checks and setup."""
    try:
        # Check Ollama server
        if not check_ollama_server():
            print("Ollama server not detected. Please install and start Ollama:")
            print("1. Download from: https://ollama.ai/download")
            print("2. Install and start the Ollama service")
            print("3. Run 'ollama serve' in a terminal")
            return False
        
        # Check LLaMA model
        if not check_llama_model():
            print("LLaMA 2 model not found. Please pull it using:")
            print("ollama pull llama2")
            return False
        
        # Initialize database
        if not ensure_database():
            print("Failed to initialize database. Please check logs for details.")
            return False
        
        # Create necessary directories
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("models").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        
        # Speak welcome message
        speak_welcome()
        
        return True
    
    except Exception as e:
        logger.error(f"First-run checks failed: {str(e)}")
        return False

def main():
    """Main entry point when run as a module."""
    try:
        logger.info("Starting Zara Assistant...")
        
        # Perform first-run checks
        if not first_run_checks():
            logger.error("First-run checks failed. Please address the issues and try again.")
            sys.exit(1)
        
        # Initialize components
        agent = get_agent()
        voice = get_voice_interface()
        
        logger.info("Zara Assistant started successfully")
        
        # Main interaction loop
        while True:
            try:
                # Listen for user input
                user_input = voice.listen()
                if user_input:
                    # Process through agent
                    response = agent.process_message(user_input)
                    # Speak response
                    voice.speak(response)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                error_msg = "I encountered an error. Please try again."
                voice.speak(error_msg)
    
    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()