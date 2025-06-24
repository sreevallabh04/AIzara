# -*- coding: utf-8 -*-
"""
Enhanced Voice Interface for Zara Assistant

Features:
- Wake word detection ("Zara")
- Conversational flow with natural responses
- Better error handling and user feedback
- Continuous listening mode
- Context-aware responses
"""

import os
import time
import wave
import pyaudio
import numpy as np
import threading
import queue
from typing import Optional, Dict, List, Callable
import pyttsx3
from faster_whisper import WhisperModel
import webrtcvad
from pathlib import Path
import json
import asyncio
import re
from datetime import datetime

from .logger import get_logger
from .memory import get_memory_manager

logger = get_logger()
memory = get_memory_manager()

class ConversationState:
    """Manages conversation state and context."""
    
    def __init__(self):
        self.is_active = False
        self.wake_word_detected = False
        self.last_interaction = None
        self.conversation_context = []
        self.waiting_for_response = False
        self.user_name = None
        self.session_start = datetime.now()
    
    def start_conversation(self):
        """Start a new conversation session."""
        self.is_active = True
        self.wake_word_detected = True
        self.last_interaction = datetime.now()
        logger.info("Conversation started")
    
    def end_conversation(self):
        """End the current conversation session."""
        self.is_active = False
        self.wake_word_detected = False
        self.waiting_for_response = False
        logger.info("Conversation ended")
    
    def add_interaction(self, user_input: str, response: str):
        """Add an interaction to the conversation context."""
        self.conversation_context.append({
            'timestamp': datetime.now(),
            'user': user_input,
            'assistant': response
        })
        self.last_interaction = datetime.now()
        
        # Keep only last 5 interactions for context
        if len(self.conversation_context) > 5:
            self.conversation_context.pop(0)
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation context."""
        if not self.conversation_context:
            return "No previous context."
        
        context_lines = []
        for interaction in self.conversation_context[-3:]:  # Last 3 interactions
            context_lines.append(f"User: {interaction['user']}")
            context_lines.append(f"Assistant: {interaction['assistant']}")
        
        return "\n".join(context_lines)

class WakeWordDetector:
    """Detects the wake word 'Zara' in audio input."""
    
    def __init__(self):
        self.wake_words = ['zara', 'sarah', 'sara', 'clara', 'zahra']  # Variations for voice recognition
        self.confidence_threshold = 0.6
    
    def detect_wake_word(self, text: str) -> bool:
        """Check if the wake word is present in the text."""
        if not text:
            return False
        
        text_lower = text.lower().strip()
        
        # Direct matches
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                logger.info(f"Wake word detected: '{wake_word}' in '{text}'")
                return True
        
        # Check for wake word at the beginning of the sentence
        words = text_lower.split()
        if words and any(word in self.wake_words for word in words[:2]):
            logger.info(f"Wake word detected at start: '{text}'")
            return True
        
        return False
    
    def extract_command_after_wake_word(self, text: str) -> Optional[str]:
        """Extract the command that comes after the wake word."""
        if not text:
            return None
        
        text_lower = text.lower().strip()
        
        # Try to find and remove the wake word
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                # Split on the wake word and take everything after it
                parts = text_lower.split(wake_word, 1)
                if len(parts) > 1:
                    command = parts[1].strip()
                    # Remove common filler words
                    command = re.sub(r'^(please|can you|could you|would you)', '', command).strip()
                    if command:
                        return command
        
        return text  # Return original if no wake word found

class EnhancedVoiceInterface:
    """Enhanced voice interface with conversational AI capabilities."""
    
    def __init__(self):
        self.config = self._load_config()
        self.conversation = ConversationState()
        self.wake_detector = WakeWordDetector()
        
        # Audio setup
        self.audio = pyaudio.PyAudio()
        self.input_device_index = self._select_input_device()
        
        # Speech engines
        self._setup_whisper()
        self._setup_tts()
        self._setup_vad()
        
        # Audio directory
        self.audio_dir = Path("data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Conversation responses
        self.setup_conversational_responses()
        
        # Listening control
        self.is_listening = False
        self.stop_listening = False
        
        logger.info("Enhanced voice interface initialized")
    
    def _load_config(self) -> Dict:
        """Load voice configuration."""
        config_path = Path("config/voice_config.json")
        default_config = {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "format": pyaudio.paInt16,
            "whisper_model": "base",
            "speech_rate": 175,
            "volume": 0.9,
            "vad_mode": 2,
            "recording_duration": 8.0,
            "wake_word_timeout": 45.0,  # Seconds to wait for wake word
            "conversation_timeout": 300.0,  # 5 minutes conversation timeout
            "wake_word_chunk_duration": 5.0,  # Longer chunks for wake word detection
            "command_duration": 10.0  # Even longer for commands
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    return {**default_config, **loaded_config}
            else:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return default_config
    
    def _select_input_device(self) -> Optional[int]:
        """Select the best available input device."""
        try:
            device_count = self.audio.get_device_count()
            
            # Look for working input devices
            for i in range(device_count):
                try:
                    info = self.audio.get_device_info_by_index(i)
                    if info.get('maxInputChannels', 0) > 0:
                        # Test if device works
                        test_stream = self.audio.open(
                            format=self.config['format'],
                            channels=self.config['channels'],
                            rate=self.config['sample_rate'],
                            input=True,
                            input_device_index=i,
                            frames_per_buffer=self.config['chunk_size']
                        )
                        test_stream.close()
                        logger.info(f"Selected input device: {info['name']}")
                        return i
                except Exception:
                    continue
            
            logger.error("No working input device found")
            return None
        except Exception as e:
            logger.error(f"Error selecting input device: {e}")
            return None
    
    def _setup_whisper(self):
        """Initialize Whisper model."""
        try:
            self.whisper = WhisperModel(
                self.config["whisper_model"],
                device="cpu",
                compute_type="int8"
            )
            logger.info("Whisper model loaded")
        except Exception as e:
            logger.error(f"Failed to load Whisper: {e}")
            raise
    
    def _setup_tts(self):
        """Initialize text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Configure voice
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to find a female voice for Zara
                for voice in voices:
                    if any(name in voice.name.lower() for name in ['zira', 'hazel', 'female']):
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_engine.setProperty('rate', self.config['speech_rate'])
            self.tts_engine.setProperty('volume', self.config['volume'])
            
            logger.info("TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            raise
    
    def _setup_vad(self):
        """Initialize Voice Activity Detection."""
        try:
            self.vad = webrtcvad.Vad(self.config['vad_mode'])
            logger.info("VAD initialized")
        except Exception as e:
            logger.warning(f"VAD initialization failed: {e}")
            self.vad = None
    
    def setup_conversational_responses(self):
        """Setup conversational response templates."""
        self.greetings = [
            "Hello! I'm Zara, your personal assistant. How can I help you today?",
            "Hi there! Zara here, ready to assist you. What can I do for you?",
            "Hey! It's Zara. I'm here to help. What would you like me to do?",
            "Good to hear from you! I'm Zara, your AI assistant. How may I assist you?"
        ]
        
        self.acknowledgments = [
            "I'm on it!",
            "Right away!",
            "Consider it done!",
            "I'll take care of that for you!",
            "Got it! Let me help you with that."
        ]
        
        self.clarifications = [
            "I didn't quite catch that. Could you please repeat?",
            "Sorry, I didn't understand. Could you try saying that again?",
            "I'm having trouble understanding. Can you rephrase that?",
            "Could you speak a bit clearer? I want to make sure I help you correctly."
        ]
        
        self.farewells = [
            "Goodbye! Have a wonderful day!",
            "See you later! Feel free to call me anytime.",
            "Take care! I'm always here when you need me.",
            "Bye for now! Remember, just say 'Zara' to get my attention."
        ]
    
    def speak(self, text: str, interrupt_listening: bool = True):
        """Speak text with conversation context."""
        try:
            if interrupt_listening:
                self.stop_listening = True
                time.sleep(0.1)  # Brief pause to stop listening
            
            logger.info(f"Speaking: {text}")
            print(f"🤖 Zara: {text}")
            
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            if interrupt_listening:
                self.stop_listening = False
            
        except Exception as e:
            logger.error(f"Speech failed: {e}")
            print(f"🤖 Zara: {text}")  # Fallback to text
    
    def record_audio(self, duration: float = None) -> Optional[str]:
        """Record audio for specified duration."""
        if self.input_device_index is None:
            return None
        
        if duration is None:
            duration = self.config['recording_duration']
        
        frames = []
        stream = None
        
        try:
            stream = self.audio.open(
                format=self.config['format'],
                channels=self.config['channels'],
                rate=self.config['sample_rate'],
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.config['chunk_size']
            )
            
            print(f"🎤 Recording for {duration} seconds... Take your time and speak naturally!")
            
            chunks_to_record = int(self.config['sample_rate'] / self.config['chunk_size'] * duration)
            chunks_per_second = int(self.config['sample_rate'] / self.config['chunk_size'])
            
            for i in range(chunks_to_record):
                if self.stop_listening:
                    break
                try:
                    data = stream.read(self.config['chunk_size'], exception_on_overflow=False)
                    frames.append(data)
                    
                    # Show progress every second
                    if i % chunks_per_second == 0:
                        seconds_elapsed = i // chunks_per_second
                        seconds_remaining = duration - seconds_elapsed
                        if seconds_remaining > 1:
                            print(f"⏱️  {seconds_remaining:.0f} seconds remaining...")
                            
                except Exception as e:
                    logger.warning(f"Audio read error: {e}")
            
            print("🎤 Recording complete! Processing your speech...")
            
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            return None
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception:
                    pass
        
        if not frames:
            return None
        
        # Save audio file
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            audio_path = self.audio_dir / f"recording_{timestamp}.wav"
            
            with wave.open(str(audio_path), 'wb') as wf:
                wf.setnchannels(self.config['channels'])
                wf.setsampwidth(self.audio.get_sample_size(self.config['format']))
                wf.setframerate(self.config['sample_rate'])
                wf.writeframes(b''.join(frames))
            
            return str(audio_path)
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None
    
    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio file to text."""
        try:
            segments, _ = self.whisper.transcribe(audio_path)
            text = " ".join([seg.text for seg in segments]).strip()
            
            if text:
                logger.info(f"Transcribed: {text}")
                return text
            else:
                logger.warning("No speech transcribed")
                return None
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def listen_for_wake_word(self) -> bool:
        """Listen continuously for the wake word 'Zara'."""
        print("\n👂 Listening for 'Zara'... (Say 'Zara' to get my attention)")
        print("💡 Tip: I listen for 5 seconds at a time, so speak at your natural pace!")
        print("Press Ctrl+C to exit")
        
        start_time = time.time()
        timeout = self.config['wake_word_timeout']
        
        while not self.stop_listening:
            try:
                # Check timeout
                if time.time() - start_time > timeout:
                    return False
                
                # Record a longer audio snippet for wake word detection
                audio_path = self.record_audio(self.config['wake_word_chunk_duration'])  # 5 second chunks
                if not audio_path:
                    continue
                
                # Transcribe
                text = self.transcribe_audio(audio_path)
                if not text:
                    continue
                
                print(f"🎤 Heard: '{text}'")
                
                # Check for wake word
                if self.wake_detector.detect_wake_word(text):
                    print("✨ Wake word detected!")
                    
                    # Extract command after wake word
                    command = self.wake_detector.extract_command_after_wake_word(text)
                    if command and len(command) > 3:  # Meaningful command
                        print(f"💬 Command detected: '{command}'")
                        return command
                    else:
                        return True  # Wake word only
                
                # Clean up audio file
                try:
                    os.remove(audio_path)
                except Exception:
                    pass
                    
            except KeyboardInterrupt:
                return False
            except Exception as e:
                logger.error(f"Wake word detection error: {e}")
                time.sleep(0.5)
        
        return False
    
    def listen_for_command(self) -> Optional[str]:
        """Listen for a user command during conversation."""
        print("\n🎤 What can I help you with?")
        print("💬 You have 10 seconds to speak comfortably...")
        
        audio_path = self.record_audio(self.config['command_duration'])  # 10 seconds for commands
        if not audio_path:
            return None
        
        text = self.transcribe_audio(audio_path)
        
        # Clean up audio file
        try:
            os.remove(audio_path)
        except Exception:
            pass
        
        if text:
            print(f"💬 You said: '{text}'")
            return text
        else:
            print("❌ I didn't hear anything. Please try again.")
            return None
    
    def handle_conversation_flow(self, user_input: str) -> str:
        """Handle conversational flow and generate appropriate responses."""
        # Import here to avoid circular imports
        from .agent import get_agent
        
        # Check for conversation control commands
        user_lower = user_input.lower().strip()
        
        if any(word in user_lower for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
            self.conversation.end_conversation()
            return np.random.choice(self.farewells)
        
        if any(word in user_lower for word in ['hello', 'hi', 'hey']) and len(user_input.split()) <= 2:
            return np.random.choice(self.greetings)
        
        # Get AI response
        try:
            agent = get_agent()
            
            # Run the agent's process_message synchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response = loop.run_until_complete(agent.process_message(user_input))
            finally:
                loop.close()
            
            if response:
                return response
            else:
                return "I'm not sure how to help with that. Could you try asking in a different way?"
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm having trouble processing that right now. Could you please try again?"
    
    def start_conversation_loop(self):
        """Start the main conversation loop."""
        self.speak(np.random.choice(self.greetings))
        self.conversation.start_conversation()
        
        try:
            while self.conversation.is_active:
                # Listen for user input
                user_input = self.listen_for_command()
                
                if not user_input:
                    self.speak(np.random.choice(self.clarifications))
                    continue
                
                # Generate response
                response = self.handle_conversation_flow(user_input)
                
                # Speak response
                self.speak(response)
                
                # Update conversation context
                self.conversation.add_interaction(user_input, response)
                
                # Check if conversation should end
                if not self.conversation.is_active:
                    break
                    
        except KeyboardInterrupt:
            self.conversation.end_conversation()
            self.speak("Goodbye!")
        except Exception as e:
            logger.error(f"Conversation error: {e}")
            self.speak("I encountered an error. Goodbye for now!")
    
    def run(self):
        """Main run loop with wake word detection."""
        print("🤖 Zara Assistant - Enhanced Voice Interface")
        print("=" * 60)
        print("Say 'Zara' to get my attention!")
        print("Or say 'Zara [command]' to give a direct command.")
        print("Press Ctrl+C to exit.")
        print("=" * 60)
        
        try:
            while True:
                # Listen for wake word
                wake_result = self.listen_for_wake_word()
                
                if wake_result is False:
                    break  # Timeout or exit
                elif isinstance(wake_result, str):
                    # Direct command detected
                    print(f"🚀 Processing direct command: '{wake_result}'")
                    response = self.handle_conversation_flow(wake_result)
                    self.speak(response)
                else:
                    # Just wake word, start conversation
                    print("🗣️ Starting conversation...")
                    self.start_conversation_loop()
                
                # Brief pause before listening again
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Shutting down Zara Assistant. Goodbye!")
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            print(f"❌ Error: {e}")
        finally:
            if hasattr(self, 'audio'):
                self.audio.terminate()

def run_enhanced_voice():
    """Run the enhanced voice interface."""
    try:
        voice_interface = EnhancedVoiceInterface()
        voice_interface.run()
    except Exception as e:
        logger.error(f"Failed to start enhanced voice interface: {e}")
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    run_enhanced_voice() 