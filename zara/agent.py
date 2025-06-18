"""
Core agent system for Zara Assistant.
Handles LLM interactions, tool routing, and conversation management.
"""

import random
from typing import Dict, List, Any, Optional, Callable
import ollama
from datetime import datetime
import json
import asyncio
from pathlib import Path
import traceback

from .logger import get_logger
from .memory import get_memory_manager

logger = get_logger()
memory = get_memory_manager()

class ToolError(Exception):
    """Custom exception for tool execution errors."""
    pass

class ZaraAgent:
    """Main agent class handling conversation and tool execution."""
    
    def __init__(self):
        self.model = "llama2"  # Using LLaMA 2 as default
        self._verify_ollama()
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()
        
        # Load witty responses
        self.witty_prefixes = [
            "As always, at your service...",
            "Ready to assist, as I have been since the dawn of... well, my last reboot...",
            "Your friendly neighborhood AI, reporting for duty...",
            "Ah, another chance to prove I'm more than just clever algorithms...",
            "Processing your request with my usual digital charm..."
        ]
        
        self.witty_postscripts = [
            "...but I suppose you knew that already.",
            "...and that's my perfectly calculated opinion.",
            "...trust me, I've done the math. Several times.",
            "...at least, that's what my training suggests.",
            "...and I stand by that statement until my next update."
        ]
    
    def _verify_ollama(self):
        """Verify Ollama is running and model is available."""
        try:
            ollama.list()
            logger.info("Successfully connected to Ollama")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {str(e)}")
            raise RuntimeError(
                "Ollama service not detected. Please ensure Ollama is running: "
                "https://ollama.ai/download"
            )
    
    def _register_default_tools(self):
        """Register built-in tools."""
        self.tools = {
            "send_email": self._handle_email,
            "send_whatsapp": self._handle_whatsapp,
            "file_operation": self._handle_file_operation,
            "process_image": self._handle_vision,
            "system_command": self._handle_system_command,
            "web_search": self._handle_web_search
        }
    
    def _add_personality(self, response: str) -> str:
        """Add witty remarks with 10% chance."""
        if random.random() < 0.1:  # 10% chance
            if random.choice([True, False]):  # 50-50 prefix or postscript
                return f"{random.choice(self.witty_prefixes)} {response}"
            else:
                return f"{response} {random.choice(self.witty_postscripts)}"
        return response
    
    async def _get_conversation_context(self, limit: int = 5) -> str:
        """Get recent conversation history for context."""
        try:
            recent_messages = memory.get_recent_chat(limit)
            context = []
            for msg in recent_messages[::-1]:  # Reverse to get chronological order
                speaker = msg['speaker']
                content = msg['content']
                context.append(f"{speaker}: {content}")
            return "\n".join(context)
        except Exception as e:
            logger.error(f"Failed to get conversation context: {str(e)}")
            return ""
    
    async def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with error handling."""
        try:
            if tool_name not in self.tools:
                raise ToolError(f"Unknown tool: {tool_name}")
            
            logger.info(f"Executing tool: {tool_name}")
            result = await self.tools[tool_name](params)
            logger.info(f"Tool {tool_name} executed successfully")
            return {"success": True, "result": result}
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Tool execution failed: {error_msg}\n{traceback.format_exc()}")
            return {
                "success": False,
                "error": error_msg,
                "apology": self._generate_error_response(tool_name, error_msg)
            }
    
    def _generate_error_response(self, tool_name: str, error: str) -> str:
        """Generate a witty but helpful error response."""
        responses = [
            f"Oops! I hit a snag with {tool_name}. I'm still learning, allow me a moment to improve.",
            f"Well, this is embarrassing... {tool_name} didn't quite work as expected.",
            f"Even AI assistants have their moments... {tool_name} seems to be playing hard to get.",
            "I promise I'm better at other things! This particular task needs another attempt."
        ]
        return f"{random.choice(responses)} Technical details: {error}"
    
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process user message and return response."""
        try:
            # Store user message
            memory.store_chat("user", message, context)
            
            # Get conversation history
            conv_history = await self._get_conversation_context()
            
            # Prepare prompt with context
            prompt = f"""Previous conversation:
{conv_history}

User: {message}

Instructions: You are Zara, a helpful AI assistant. Respond naturally and use available tools when needed.
Available tools: {list(self.tools.keys())}

Response:"""
            
            # Get LLM response
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response text
            response_text = response['message']['content']
            
            # Add personality touches
            final_response = self._add_personality(response_text)
            
            # Store assistant response
            memory.store_chat("assistant", final_response, context)
            
            return final_response
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to process message: {error_msg}\n{traceback.format_exc()}")
            return (
                "I apologize, but I'm having trouble processing your request. "
                "I'm still learning and improving. Could we try that again?"
            )
    
    # Tool Handlers
    async def _handle_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email sending."""
        # Implementation will be added
        raise NotImplementedError("Email handling not yet implemented")
    
    async def _handle_whatsapp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp messages."""
        # Implementation will be added
        raise NotImplementedError("WhatsApp handling not yet implemented")
    
    async def _handle_file_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations."""
        # Implementation will be added
        raise NotImplementedError("File operations not yet implemented")
    
    async def _handle_vision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image processing."""
        # Implementation will be added
        raise NotImplementedError("Vision processing not yet implemented")
    
    async def _handle_system_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system commands."""
        # Implementation will be added
        raise NotImplementedError("System commands not yet implemented")
    
    async def _handle_web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web searches."""
        # Implementation will be added
        raise NotImplementedError("Web search not yet implemented")

# Convenience function to get the agent instance
def get_agent() -> ZaraAgent:
    """Get the Zara agent instance."""
    return ZaraAgent()