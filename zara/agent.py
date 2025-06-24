"""
Core agent system for Zara Assistant.
Handles LLM interactions, tool routing, and conversation management.
"""

import random
import re
import os
import webbrowser
import subprocess
from typing import Dict, List, Any, Optional, Callable, Tuple, Pattern
import ollama
from datetime import datetime
import json
import asyncio
from pathlib import Path
import traceback

from .logger import get_logger
from .memory import get_memory_manager
from . import tools

logger = get_logger()
memory = get_memory_manager()

class ToolError(Exception):
    """Custom exception for tool execution errors."""
    pass

class ZaraAgent:
    """Main agent class handling conversation and tool execution."""
    
    def __init__(self):
        self.model = "llama3.2"  # Using LLaMA 3.2 as default
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
            "web_search": self._handle_web_search,
            "open_website": self._handle_open_website,
            "open_application": self._handle_open_application,
            "play_media": self._handle_play_media
        }
        
        # Register direct command patterns for instant responses with fuzzy matching for voice recognition
        self._command_patterns = [
            # Contact-based email patterns (highest priority)
            (re.compile(r"send\s+(?:an?\s+)?email\s+to\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$", re.IGNORECASE), 
             self._direct_send_email_to_contact),
            
            (re.compile(r"email\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$", re.IGNORECASE), 
             self._direct_send_email_to_contact),
            
            (re.compile(r"compose\s+(?:an?\s+)?email\s+to\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$", re.IGNORECASE), 
             self._direct_send_email_to_contact),
             
            (re.compile(r"write\s+(?:an?\s+)?email\s+to\s+([a-zA-Z\s]+?)(?:\s+about\s+(.+?))?(?:\s+saying\s+(.+?))?$", re.IGNORECASE), 
             self._direct_send_email_to_contact),
            
            # General email patterns (lower priority)
            (re.compile(r"send\s+(?:an?\s+)?email", re.IGNORECASE), 
             self._direct_send_email),
            
            (re.compile(r"compose\s+(?:an?\s+)?email", re.IGNORECASE), 
             self._direct_send_email),
             
            (re.compile(r"write\s+(?:an?\s+)?email", re.IGNORECASE), 
             self._direct_send_email),
             
            (re.compile(r"email\s+someone", re.IGNORECASE), 
             self._direct_send_email),
            
            # Contact management patterns
            (re.compile(r"add\s+contact\s+([a-zA-Z\s]+?)(?:\s+phone\s+([+\d\s\-()]+?))?(?:\s+email\s+([\w\.\-_]+@[\w\.\-_]+))?", re.IGNORECASE), 
             self._direct_add_contact),
             
            (re.compile(r"show\s+(?:all\s+)?contacts", re.IGNORECASE), 
             self._direct_list_contacts),
             
            (re.compile(r"list\s+(?:all\s+)?contacts", re.IGNORECASE), 
             self._direct_list_contacts),
             
            (re.compile(r"find\s+contact\s+([a-zA-Z\s]+)", re.IGNORECASE), 
             self._direct_get_contact),
            
            # Open website patterns with common speech recognition variations
            (re.compile(r"open\s+(youtube|you ?tube|your ?tube|google|gmail|face ?book|twitter|git ?hub|net ?flix|amazon)", re.IGNORECASE), 
             self._direct_open_website),
            
            # Open website with .com/.org/etc.
            (re.compile(r"open\s+(\w+\.\w+)(?:\s+website)?", re.IGNORECASE), 
             self._direct_open_website),
            
            # Open application patterns with variations
            (re.compile(r"open\s+(chrome|google chrome|firefox|edge|notepad|word|excel|power ?point|calculator|paint)", re.IGNORECASE), 
             self._direct_open_application),
            
            # Launch variations (for "launch" instead of "open")
            (re.compile(r"launch\s+(youtube|you ?tube|your ?tube|google|chrome|firefox|notepad|calculator)", re.IGNORECASE),
             self._direct_open_any),
            
            # Start variations (for "start" instead of "open")
            (re.compile(r"start\s+(youtube|you ?tube|your ?tube|google|chrome|firefox|notepad|calculator)", re.IGNORECASE),
             self._direct_open_any),
            
            # Search patterns
            (re.compile(r"search\s+(?:for\s+)?(.*?)(?:\s+on\s+google)?", re.IGNORECASE), 
             self._direct_search),
            
            # Play music/video patterns
            (re.compile(r"play\s+(music|youtube|you ?tube|your ?tube|spotify)", re.IGNORECASE), 
             self._direct_play_media),
             
            # Go to website shorthand (without explicit "open")
            (re.compile(r"(?:go\sto|visit)\s+(youtube|you ?tube|your ?tube|google|facebook|amazon)", re.IGNORECASE),
             self._direct_open_website)
        ]
        
        # Common speech recognition corrections
        self._common_corrections = {
            "your tube": "youtube",
            "you tube": "youtube",
            "face book": "facebook",
            "git hub": "github",
            "net flix": "netflix",
            "power point": "powerpoint",
            "google chrome": "chrome"
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
            
            # First check for direct command patterns for instant response
            direct_result = await self._check_direct_commands(message)
            if direct_result:
                action, response = direct_result
                logger.info(f"Direct command executed: {action}")
                
                # Store the response to the direct command
                memory.store_chat("assistant", response, context)
                return response
            
            # If no direct command matches, use LLM for complex queries
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
    
    async def _check_direct_commands(self, message: str) -> Optional[Tuple[str, str]]:
        """
        Check for direct command patterns and execute immediately if found.
        Returns (action, response) tuple if a command is executed, None otherwise.
        """
        for pattern, handler in self._command_patterns:
            match = pattern.search(message)
            if match:
                return await handler(match, message)
        return None
    
    def _correct_speech_recognition(self, text: str) -> str:
        """
        Apply corrections to common speech recognition errors.
        """
        corrected = text.lower()
        for error, correction in self._common_corrections.items():
            corrected = corrected.replace(error, correction)
        return corrected
    
    async def _direct_open_website(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly open a website based on the command.
        """
        site = match.group(1).lower()
        
        # Apply speech recognition corrections
        site = self._correct_speech_recognition(site)
        
        # Handle common websites
        if '.' not in site:
            common_sites = {
                'youtube': 'https://www.youtube.com',
                'google': 'https://www.google.com',
                'gmail': 'https://mail.google.com',
                'facebook': 'https://www.facebook.com',
                'twitter': 'https://twitter.com',
                'github': 'https://github.com',
                'netflix': 'https://www.netflix.com',
                'amazon': 'https://www.amazon.com'
            }
            url = common_sites.get(site, f"https://www.{site}.com")
        else:
            # If it already has a domain (.com, .org, etc.)
            url = f"https://{site}" if not site.startswith('http') else site
        
        try:
            webbrowser.open(url)
            return "open_website", f"Opening {site}"
        except Exception as e:
            logger.error(f"Failed to open website: {str(e)}")
            return "open_website_error", f"I tried to open {site}, but encountered an error: {str(e)}"
    
    async def _direct_open_any(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Intelligently determine if the target is a website or application and open it.
        """
        target = match.group(1).lower()
        
        # Apply speech recognition corrections
        target = self._correct_speech_recognition(target)
        
        # Check if it's a common website first
        common_websites = ['youtube', 'google', 'gmail', 'facebook', 'twitter', 'github', 'netflix', 'amazon']
        if target in common_websites:
            return await self._direct_open_website(match, message)
        
        # Otherwise, treat as application
        return await self._direct_open_application(match, message)
    
    async def _direct_open_application(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly open an application based on the command.
        """
        app = match.group(1).lower()
        
        # Apply speech recognition corrections
        app = self._correct_speech_recognition(app)
        try:
            result = tools.open_app(app)
            return "open_application", result
        except Exception as e:
            logger.error(f"Failed to open application: {str(e)}")
            return "open_application_error", f"I tried to open {app}, but encountered an error: {str(e)}"
    
    async def _direct_search(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly perform a search based on the command.
        """
        query = match.group(1)
        try:
            result = tools.search_google(query)
            return "web_search", result
        except Exception as e:
            logger.error(f"Failed to search: {str(e)}")
            return "web_search_error", f"I tried to search for {query}, but encountered an error: {str(e)}"
    
    async def _direct_play_media(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly play media based on the command.
        """
        source = match.group(1).lower()
        
        # Apply speech recognition corrections
        source = self._correct_speech_recognition(source)
        try:
            result = tools.play_music(source)
            return "play_media", result
        except Exception as e:
            logger.error(f"Failed to play media: {str(e)}")
            return "play_media_error", f"I tried to play {source}, but encountered an error: {str(e)}"
    
    async def _direct_send_email(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly handle email sending with web automation.
        """
        try:
            # Use the web automation email system
            result = tools.send_email()
            return "send_email", result
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return "send_email_error", f"I tried to help you send an email, but encountered an error: {str(e)}"
    
    async def _direct_send_email_to_contact(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly handle email sending to a specific contact.
        """
        try:
            contact_name = match.group(1).strip()
            subject = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else None
            body = match.group(3).strip() if len(match.groups()) > 2 and match.group(3) else None
            
            # Use the contact-based email system
            result = tools.send_email_to_contact(contact_name, subject, body)
            return "send_email_to_contact", result
            
        except Exception as e:
            logger.error(f"Failed to send email to contact: {str(e)}")
            return "send_email_to_contact_error", f"I tried to send an email to the contact, but encountered an error: {str(e)}"
    
    async def _direct_add_contact(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly handle adding a new contact.
        """
        try:
            name = match.group(1).strip()
            phone = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else ""
            email = match.group(3).strip() if len(match.groups()) > 2 and match.group(3) else ""
            
            result = tools.add_contact(name, phone, email)
            return "add_contact", result
            
        except Exception as e:
            logger.error(f"Failed to add contact: {str(e)}")
            return "add_contact_error", f"I tried to add the contact, but encountered an error: {str(e)}"
    
    async def _direct_list_contacts(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly handle listing all contacts.
        """
        try:
            result = tools.list_contacts()
            return "list_contacts", result
            
        except Exception as e:
            logger.error(f"Failed to list contacts: {str(e)}")
            return "list_contacts_error", f"I tried to list your contacts, but encountered an error: {str(e)}"
    
    async def _direct_get_contact(self, match: re.Match, message: str) -> Tuple[str, str]:
        """
        Directly handle getting a specific contact.
        """
        try:
            contact_name = match.group(1).strip()
            result = tools.get_contact(contact_name)
            return "get_contact", result
            
        except Exception as e:
            logger.error(f"Failed to get contact: {str(e)}")
            return "get_contact_error", f"I tried to find the contact, but encountered an error: {str(e)}"
    
    # Tool Handlers
    async def _handle_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email sending."""
        try:
            to = params.get('to', '')
            subject = params.get('subject', '')
            body = params.get('body', '')
            result = tools.send_email(to, subject, body)
            return {"status": "success", "message": result}
        except Exception as e:
            logger.error(f"Email handling error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_whatsapp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle WhatsApp messages."""
        try:
            contact = params.get('contact', '')
            message = params.get('message', '')
            result = tools.send_whatsapp_message(contact, message)
            return {"status": "success", "message": result}
        except Exception as e:
            logger.error(f"WhatsApp handling error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_file_operation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations."""
        try:
            operation = params.get('operation', '')
            path = params.get('path', '')
            
            if operation == 'open':
                result = tools.open_file(path)
                return {"status": "success", "message": result}
            else:
                return {"status": "error", "message": f"Unknown operation: {operation}"}
        except Exception as e:
            logger.error(f"File operation error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_vision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image processing."""
        try:
            action = params.get('action', '')
            
            if action == 'capture':
                result = tools.capture_image()
                return {"status": "success", "message": result}
            elif action == 'describe':
                image_path = params.get('path', '')
                result = tools.describe_image(image_path)
                return {"status": "success", "message": result}
            else:
                return {"status": "error", "message": f"Unknown vision action: {action}"}
        except Exception as e:
            logger.error(f"Vision processing error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_system_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system commands."""
        try:
            command_type = params.get('type', '')
            
            if command_type == 'open_app':
                app_name = params.get('app_name', '')
                result = tools.open_app(app_name)
                return {"status": "success", "message": result}
            else:
                return {"status": "error", "message": f"Unknown system command: {command_type}"}
        except Exception as e:
            logger.error(f"System command error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web searches."""
        try:
            query = params.get('query', '')
            result = tools.search_google(query)
            return {"status": "success", "message": result}
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_open_website(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opening websites."""
        try:
            url = params.get('url', '')
            if not url.startswith(('http://', 'https://')):
                url = f"https://{url}"
            
            webbrowser.open(url)
            return {"status": "success", "message": f"Opening website: {url}"}
        except Exception as e:
            logger.error(f"Website opening error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_open_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opening applications."""
        try:
            app_name = params.get('app_name', '')
            result = tools.open_app(app_name)
            return {"status": "success", "message": result}
        except Exception as e:
            logger.error(f"Application opening error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _handle_play_media(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle playing media."""
        try:
            source = params.get('source', '')
            result = tools.play_music(source)
            return {"status": "success", "message": result}
        except Exception as e:
            logger.error(f"Media playing error: {str(e)}")
            return {"status": "error", "message": str(e)}

# Convenience function to get the agent instance
def get_agent() -> ZaraAgent:
    """Get the Zara agent instance."""
    return ZaraAgent()