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
import asyncio
import contextlib

from .logger import get_logger
from .memory import get_memory_manager

logger = get_logger()
memory = get_memory_manager()

class VoiceConfig:
    """Voice interface configuration."""
    DEFAULT_CONFIG = {
        "input_timeout": 10.0,  # seconds - increased for more user speaking time
        "vad_mode": 2,  # 0-3, higher = more aggressive (reduced from 3 to 2 for better sensitivity)
        "silence_threshold": 0.3,  # seconds - increased to allow for natural pauses
        "bypass_vad": True,  # Skip VAD processing entirely if True - safer default when VAD has issues
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
    """
    Manages speech recognition and synthesis for Zara Assistant.
    This version is refactored for maximum robustness, maintainability, and clarity.
    - Enumerates all input devices and tries each until one works.
    - Validates format support for each device.
    - Provides clear user and developer feedback.
    - Modular and testable.
    """
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
        self.audio = pyaudio.PyAudio()
        self.input_device_index = self._select_input_device()
        self._setup_whisper()
        self._setup_tts()
        self._setup_vad()
        
        # Create audio directory
        self.audio_dir = Path("data/audio")
        self.audio_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_audio(self):
        """Initialize PyAudio and select a valid input device."""
        try:
            self.audio = pyaudio.PyAudio()
            logger.info("Audio interface initialized")
            # List all input devices
            device_count = self.audio.get_device_count()
            input_devices = []
            for i in range(device_count):
                info = self.audio.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    input_devices.append((i, info['name']))
            if not input_devices:
                logger.error("No input devices found. Please connect a microphone.")
                self.input_device_index = None
            else:
                # Prefer default input device if available
                try:
                    default_index = self.audio.get_default_input_device_info()['index']
                    self.input_device_index = default_index
                    logger.info(f"Using default input device: {input_devices[default_index][1]} (index {default_index})")
                except Exception:
                    # Fallback to first available input device
                    self.input_device_index = input_devices[0][0]
                    logger.info(f"Using first available input device: {input_devices[0][1]} (index {input_devices[0][0]})")
        except Exception as e:
            logger.error(f"Failed to initialize audio: {str(e)}")
            self.input_device_index = None
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
    
    def _enumerate_input_devices(self):
        """Return a list of all available input devices with their properties."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                devices.append((i, info))
        return devices

    def _select_input_device(self):
        """
        Try all available input devices and select the first one that supports the required format.
        Returns the device index, or None if none are suitable.
        """
        required_format = self.config.config['format']
        required_channels = self.config.config['channels']
        required_rate = self.config.config['sample_rate']
        devices = self._enumerate_input_devices()
        if not devices:
            logger.critical("No input devices found. Please connect a microphone.")
            return None
        for idx, info in devices:
            try:
                # Try opening a stream to validate support
                with contextlib.closing(self.audio.open(
                    format=required_format,
                    channels=required_channels,
                    rate=required_rate,
                    input=True,
                    input_device_index=idx,
                    frames_per_buffer=self.config.config['chunk_size']
                )):
                    logger.info(f"Selected input device: {info['name']} (index {idx})")
                    return idx
            except Exception as e:
                logger.warning(f"Device {info['name']} (index {idx}) not suitable: {e}")
        logger.critical("No suitable input device found. Please check your microphone and system settings.")
        return None

    def _is_input_device_available(self):
        """Check if a valid input device is available."""
        return self.input_device_index is not None

    def _record_audio(self) -> Tuple[bool, Optional[str]]:
        """
        Record audio with appropriate method based on configuration.
        Returns (success, path_or_error).
        """
        if not self._is_input_device_available():
            logger.error("No valid input device available. Please connect a microphone and restart.")
            return False, "No valid input device available. Please connect a microphone and restart."
        
        # Check if we should bypass VAD entirely
        if self.config.config.get("bypass_vad", True):
            # Use simple recording by default - more reliable across different hardware setups
            return self._record_simple()
        else:
            # Try with VAD first, then fallback to simpler recording if needed
            success, result = self._record_with_vad()
            if success:
                return success, result
            
            # If VAD-based recording failed, try simple recording without VAD
            logger.warning(f"VAD-based recording failed: {result}. Falling back to simple recording.")
            print("Using fallback recording mode...")
            return self._record_simple()
    
    def _record_with_vad(self) -> Tuple[bool, Optional[str]]:
        """
        Record audio using Voice Activity Detection.
        Returns (success, path_or_error).
        """
        frames = []
        silent_chunks = 0
        recording = False
        start_time = time.time()
        stream = None
        try:
            stream = self.audio.open(
                format=self.config.config['format'],
                channels=self.config.config['channels'],
                rate=self.config.config['sample_rate'],
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.config.config['chunk_size']
            )
            logger.info(f"Audio stream opened successfully on device index {self.input_device_index}")
            
            # Warm up the microphone by discarding frames
            print("Warming up microphone...")
            for _ in range(20):  # Reduced from 30 to 20 frames to avoid excessive warmup
                try:
                    stream.read(self.config.config['chunk_size'], exception_on_overflow=False)
                    time.sleep(0.01)  # Small delay between frames
                except Exception as e:
                    logger.warning(f"Warm-up frame discarded due to error: {str(e)}")
                    time.sleep(0.02)  # Slightly longer delay after errors
            
            print("Ready to record!")
            while True:
                # Check timeout
                if time.time() - start_time > self.config.config['input_timeout']:
                    if not frames:
                        return False, "Timeout: No speech detected"
                    break
                
                # Read audio data with retry logic
                for retry in range(3):
                    try:
                        data = stream.read(self.config.config['chunk_size'], exception_on_overflow=False)
                        break
                    except Exception as e:
                        if retry == 2:
                            logger.error(f"Error while reading audio frame after 3 retries: {str(e)}")
                            return False, f"Recording error: {str(e)}"
                        logger.warning(f"Retry {retry + 1}/3: Error while reading audio frame: {str(e)}")
                        time.sleep(0.05)  # Longer delay between retries
                
                # Safe VAD processing with explicit try/except
                try:
                    is_speech = self.vad.is_speech(data, self.config.config['sample_rate'])
                    logger.debug(f"VAD is_speech: {is_speech}")
                    
                    if is_speech:
                        if not recording:
                            recording = True
                            logger.info("Speech detected, recording...")
                        frames.append(data)
                        silent_chunks = 0
                    elif recording:
                        frames.append(data)
                        silent_chunks += 1
                        if silent_chunks > int(self.config.config['silence_threshold'] * \
                                            (self.config.config['sample_rate'] / self.config.config['chunk_size'])):
                            break
                except Exception as e:
                    logger.error(f"Error in VAD processing: {str(e)}")
                    # Still append the frame even if VAD fails
                    frames.append(data)
                    # If we've collected some frames and VAD is failing, exit the loop
                    if len(frames) > 100:  # About 3 seconds of audio
                        break
        except Exception as e:
            logger.error(f"Error during VAD recording: {str(e)}")
            return False, f"Recording error: {str(e)}"
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.warning(f"Error closing audio stream: {str(e)}")
        
        if not frames:
            return False, "No audio recorded"
        
        # Save audio file
        return self._save_audio_frames(frames)
    
    def _record_simple(self) -> Tuple[bool, Optional[str]]:
        """
        Simpler recording method that doesn't use VAD, just records for a fixed duration.
        Returns (success, path_or_error).
        """
        frames = []
        stream = None
        try:
            stream = self.audio.open(
                format=self.config.config['format'],
                channels=self.config.config['channels'],
                rate=self.config.config['sample_rate'],
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.config.config['chunk_size']
            )
            logger.info("Simple recording mode activated")
            
            # Shorter warmup for simple mode
            print("Preparing microphone...")
            for _ in range(10):
                try:
                    stream.read(self.config.config['chunk_size'], exception_on_overflow=False)
                except Exception:
                    pass
                time.sleep(0.01)
            
            # Record for a fixed duration
            recording_duration = min(self.config.config['input_timeout'], 7)  # seconds, capped at 7
            print(f"Recording for {recording_duration} seconds... Please speak now.")
            chunks_to_record = int(self.config.config['sample_rate'] / self.config.config['chunk_size'] * recording_duration)
            
            for _ in range(chunks_to_record):
                try:
                    data = stream.read(self.config.config['chunk_size'], exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    logger.warning(f"Error reading frame in simple mode: {str(e)}")
                    # Continue despite errors
            
            print("Recording complete.")
            
        except Exception as e:
            logger.error(f"Error during simple recording: {str(e)}")
            return False, f"Simple recording error: {str(e)}"
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.warning(f"Error closing audio stream: {str(e)}")
        
        if not frames:
            return False, "No audio recorded in simple mode"
        
        # Save audio file
        return self._save_audio_frames(frames)
    
    def _save_audio_frames(self, frames) -> Tuple[bool, str]:
        """
        Save recorded audio frames to a WAV file.
        Returns (success, path_or_error).
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            audio_path = self.audio_dir / f"recording_{timestamp}.wav"
            
            with wave.open(str(audio_path), 'wb') as wf:
                wf.setnchannels(self.config.config['channels'])
                wf.setsampwidth(self.audio.get_sample_size(self.config.config['format']))
                wf.setframerate(self.config.config['sample_rate'])
                wf.writeframes(b''.join(frames))
            
            logger.info(f"Audio saved to {audio_path}")
            return True, str(audio_path)
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            return False, f"Error saving audio: {str(e)}"
    
    async def listen(self, max_retries: int = 3) -> Optional[str]:
        """Record and transcribe speech with retry logic, non-blocking."""
        if not self._is_input_device_available():
            logger.error("No input device available. Cannot listen.")
            print("No microphone detected. Please connect a microphone and restart.")
            return None
            
        # Notify user we're about to listen
        print("\n" + "="*50)
        print("Getting microphone ready...")
        
        # Track failures for fallback mode
        vad_failures = 0
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Listening attempt {attempt + 1}/{max_retries}")
                
                # Prompt the user that the assistant is listening with clear visual feedback
                if self.config.config.get("bypass_vad", True):
                    print("\n👂 Listening... Please speak when prompted.")
                else:
                    print("\n👂 Listening... Please speak now. (You have up to {} seconds)".format(
                        self.config.config['input_timeout']))
                print("-"*50)
                
                # Run recording in a background thread to avoid blocking event loop
                success, result = await asyncio.to_thread(self._record_audio)
                if not success:
                    logger.warning(f"Recording failed: {result}")
                    print(f"Recording issue: {result}")
                    vad_failures += 1
                    if attempt < max_retries - 1:
                        print(f"Retrying... (attempt {attempt + 2}/{max_retries})")
                        await asyncio.sleep(1)  # Short delay before retrying
                    continue
                
                # Transcribe audio
                print("Processing your speech...")
                segments, _ = self.whisper.transcribe(result)
                text = " ".join([seg.text for seg in segments]).strip()
                if text:
                    logger.info(f"Transcribed: {text}")
                    print(f"Heard: \"{text}\"")
                    return text
                else:
                    logger.warning("No speech transcribed")
                    print("I couldn't understand what you said. Please try again.")
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

# --- TEST STUB ---
def test_enumerate_and_select_device():
    """Test device enumeration and selection logic."""
    vi = VoiceInterface()
    devices = vi._enumerate_input_devices()
    print("Available input devices:")
    for idx, info in devices:
        print(f"  {idx}: {info['name']} (channels: {info['maxInputChannels']}, default rate: {info['defaultSampleRate']})")
    print(f"Selected device index: {vi.input_device_index}")
    assert vi.input_device_index is not None, "No suitable input device found!"

# Uncomment to run the test stub directly
# if __name__ == "__main__":
#     test_enumerate_and_select_device()