"""
Voice interface for Zara Assistant.
Handles speech-to-text and text-to-speech with configurable settings.
"""

import os
import time
import wave
import pyaudio
import numpy as np
from typing import Optional, Tuple, Dict
import pyttsx3
from faster_whisper import WhisperModel
import webrtcvad
from pathlib import Path
import json
from threading import Lock

from .logger import get_logger
from .memory import get_memory_manager

logger = get_logger()
memory = get_memory_manager()

class VoiceConfig:
    """Voice interface configuration."""
    DEFAULT_CONFIG = {
        "input_timeout": 5.0,  # seconds
        "vad_mode": 3,  # 0-3, higher = more aggressive
        "silence_threshold": 0.1,  # seconds
        "speech_rate": 175,  # words per minute
        "volume": 1.0,  # 0.0-1.0
        "whisper_model": "base",  # Whisper model size
        "sample_rate": 16000,  # Hz
        "channels": 1,
        "chunk_size": 1024,
        "format": pyaudio.paInt16
    }
    
    def __init__(self):
        self.config_path = Path("config/voice_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load or create configuration file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_CONFIG, **loaded_config}
            else:
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.config_path, 'w') as f:
                    json.dump(self.DEFAULT_CONFIG, f, indent=4)
                return self.DEFAULT_CONFIG
        except Exception as e:
            logger.error(f"Failed to load voice config: {str(e)}")
            return self.DEFAULT_CONFIG
    
    def save(self):
        """Save current configuration."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save voice config: {str(e)}")

class VoiceInterface:
    """Manages speech recognition and synthesis."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize voice components."""
        self.config = VoiceConfig()
        self._setup_audio()
        self._setup_whisper()
        self._setup_tts()
        self._setup_vad()
        
        # Create audio directory
        self.audio_dir = Path("data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_audio(self):
        """Initialize PyAudio."""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("Audio interface initialized")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {str(e)}")
            raise
    
    def _setup_whisper(self):
        """Initialize Whisper model."""
        try:
            self.whisper = WhisperModel(
                self.config.config["whisper_model"],
                device="cpu",
                compute_type="int8"
            )
            logger.info(f"Whisper model '{self.config.config['whisper_model']}' loaded")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise
    
    def _setup_tts(self):
        """Initialize text-to-speech engine."""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Try to find a good Windows voice
            windows_voices = [v for v in voices if 'microsoft' in v.id.lower()]
            if windows_voices:
                # Prefer female voices if available
                female_voices = [v for v in windows_voices if 'zira' in v.id.lower()]
                chosen_voice = female_voices[0] if female_voices else windows_voices[0]
                self.tts_engine.setProperty('voice', chosen_voice.id)
            
            # Set initial properties
            self.tts_engine.setProperty('rate', self.config.config['speech_rate'])
            self.tts_engine.setProperty('volume', self.config.config['volume'])
            
            logger.info("Text-to-speech engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {str(e)}")
            raise
    
    def _setup_vad(self):
        """Initialize Voice Activity Detection."""
        try:
            self.vad = webrtcvad.Vad(self.config.config['vad_mode'])
            logger.info("VAD initialized")
        except Exception as e:
            logger.error(f"Failed to initialize VAD: {str(e)}")
            raise
    
    def _record_audio(self) -> Tuple[bool, Optional[str]]:
        """Record audio with VAD and timeout."""
        frames = []
        silent_chunks = 0
        recording = False
        start_time = time.time()
        
        stream = self.audio.open(
            format=self.config.config['format'],
            channels=self.config.config['channels'],
            rate=self.config.config['sample_rate'],
            input=True,
            frames_per_buffer=self.config.config['chunk_size']
        )
        
        try:
            while True:
                if time.time() - start_time > self.config.config['input_timeout']:
                    if not frames:
                        return False, "Timeout: No speech detected"
                    break
                
                data = stream.read(self.config.config['chunk_size'])
                is_speech = self.vad.is_speech(data, self.config.config['sample_rate'])
                
                if is_speech:
                    if not recording:
                        recording = True
                        logger.info("Speech detected, recording...")
                    frames.append(data)
                    silent_chunks = 0
                elif recording:
                    frames.append(data)
                    silent_chunks += 1
                    if silent_chunks > int(self.config.config['silence_threshold'] * 
                                        (self.config.config['sample_rate'] / self.config.config['chunk_size'])):
                        break
        
        except Exception as e:
            logger.error(f"Error during recording: {str(e)}")
            return False, f"Recording error: {str(e)}"
        
        finally:
            stream.stop_stream()
            stream.close()
        
        if not frames:
            return False, "No audio recorded"
        
        # Save audio file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        audio_path = self.audio_dir / f"recording_{timestamp}.wav"
        
        with wave.open(str(audio_path), 'wb') as wf:
            wf.setnchannels(self.config.config['channels'])
            wf.setsampwidth(self.audio.get_sample_size(self.config.config['format']))
            wf.setframerate(self.config.config['sample_rate'])
            wf.writeframes(b''.join(frames))
        
        return True, str(audio_path)
    
    async def listen(self, max_retries: int = 3) -> Optional[str]:
        """Record and transcribe speech with retry logic."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Listening attempt {attempt + 1}/{max_retries}")
                success, result = self._record_audio()
                
                if not success:
                    logger.warning(f"Recording failed: {result}")
                    continue
                
                # Transcribe audio
                segments, _ = self.whisper.transcribe(result)
                text = " ".join([seg.text for seg in segments]).strip()
                
                if text:
                    logger.info(f"Transcribed: {text}")
                    return text
                else:
                    logger.warning("No speech transcribed")
            
            except Exception as e:
                logger.error(f"Listen attempt {attempt + 1} failed: {str(e)}")
        
        return None
    
    def speak(self, text: str) -> bool:
        """Convert text to speech."""
        try:
            logger.info(f"Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS failed: {str(e)}")
            return False
    
    def set_speech_rate(self, rate: int) -> bool:
        """Set speech rate (words per minute)."""
        try:
            self.tts_engine.setProperty('rate', rate)
            self.config.config['speech_rate'] = rate
            self.config.save()
            logger.info(f"Speech rate set to {rate}")
            return True
        except Exception as e:
            logger.error(f"Failed to set speech rate: {str(e)}")
            return False
    
    def set_volume(self, volume: float) -> bool:
        """Set speech volume (0.0-1.0)."""
        try:
            self.tts_engine.setProperty('volume', volume)
            self.config.config['volume'] = volume
            self.config.save()
            logger.info(f"Volume set to {volume}")
            return True
        except Exception as e:
            logger.error(f"Failed to set volume: {str(e)}")
            return False
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'audio'):
            self.audio.terminate()
        if hasattr(self, 'tts_engine'):
            self.tts_engine.stop()

# Convenience function to get the voice interface instance
def get_voice_interface() -> VoiceInterface:
    """Get the singleton voice interface instance."""
    return VoiceInterface()