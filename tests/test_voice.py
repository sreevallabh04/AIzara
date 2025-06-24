"""
Test suite for Zara's voice interface.
Tests speech recognition and synthesis with mocked audio hardware.
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import numpy as np
import json
from pathlib import Path
import wave
import pyaudio
import tempfile
import os

from zara.voice import get_voice_interface, VoiceInterface, VoiceConfig

# Mock audio data
MOCK_AUDIO_DATA = np.zeros(16000, dtype=np.int16)  # 1 second of silence
MOCK_TRANSCRIPTION = [MagicMock(text="Hello Zara")]

@pytest.fixture
def mock_pyaudio():
    """Mock PyAudio functionality."""
    mock_stream = MagicMock()
    mock_stream.read.return_value = MOCK_AUDIO_DATA.tobytes()
    
    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream
    mock_pa.get_sample_size.return_value = 2
    
    with patch('pyaudio.PyAudio', return_value=mock_pa):
        yield mock_pa

@pytest.fixture
def mock_whisper():
    """Mock Whisper model."""
    mock_model = MagicMock()
    mock_model.transcribe.return_value = (MOCK_TRANSCRIPTION, None)
    
    with patch('faster_whisper.WhisperModel', return_value=mock_model):
        yield mock_model

@pytest.fixture
def mock_pyttsx3():
    """Mock pyttsx3 text-to-speech engine."""
    mock_engine = MagicMock()
    mock_voice = MagicMock()
    mock_voice.id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
    
    # Mock voices property
    type(mock_engine).voices = PropertyMock(return_value=[mock_voice])
    
    with patch('pyttsx3.init', return_value=mock_engine):
        yield mock_engine

@pytest.fixture
def mock_vad():
    """Mock Voice Activity Detection."""
    mock_vad = MagicMock()
    mock_vad.is_speech.return_value = True
    
    with patch('webrtcvad.Vad', return_value=mock_vad):
        yield mock_vad

@pytest.fixture
def test_config(tmp_path):
    """Create test voice configuration."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "voice_config.json"
    
    config = {
        "input_timeout": 3.0,
        "vad_mode": 2,
        "silence_threshold": 0.5,
        "speech_rate": 150,
        "volume": 0.8,
        "whisper_model": "tiny",
        "sample_rate": 16000,
        "channels": 1,
        "chunk_size": 1024,
        "format": pyaudio.paInt16
    }
    
    config_file.write_text(json.dumps(config))
    return config_file

@pytest.fixture
def test_voice(mock_pyaudio, mock_whisper, mock_pyttsx3, mock_vad, test_config, tmp_path):
    """Create test voice interface instance."""
    # Reset singleton
    VoiceInterface._instance = None
    
    # Mock paths
    with patch('pathlib.Path.exists', return_value=True), \
         patch('pathlib.Path.mkdir'):
        return get_voice_interface()

def test_voice_singleton():
    """Test that voice interface is a singleton."""
    voice1 = get_voice_interface()
    voice2 = get_voice_interface()
    assert voice1 is voice2

def test_config_loading(test_voice, test_config):
    """Test configuration loading and defaults."""
    assert test_voice.config.config["speech_rate"] == 150
    assert test_voice.config.config["vad_mode"] == 2
    assert test_voice.config.config["sample_rate"] == 16000

def test_audio_initialization(test_voice, mock_pyaudio):
    """Test audio system initialization."""
    assert hasattr(test_voice, 'audio')
    mock_pyaudio.open.assert_not_called()  # Should only open when recording

@pytest.mark.asyncio
async def test_listen_success(test_voice, mock_pyaudio):
    """Test successful speech recognition."""
    text = await test_voice.listen()
    assert text == "Hello Zara"
    assert mock_pyaudio.open.called

@pytest.mark.asyncio
async def test_listen_timeout(test_voice, mock_pyaudio):
    """Test listening timeout."""
    # Mock silent audio
    mock_pyaudio.open.return_value.read.return_value = np.zeros(1024, dtype=np.int16).tobytes()
    
    text = await test_voice.listen()
    assert text is None

def test_speak(test_voice, mock_pyttsx3):
    """Test text-to-speech functionality."""
    success = test_voice.speak("Hello")
    assert success
    mock_pyttsx3.say.assert_called_with("Hello")
    mock_pyttsx3.runAndWait.assert_called_once()

def test_speak_error(test_voice, mock_pyttsx3):
    """Test TTS error handling."""
    mock_pyttsx3.say.side_effect = Exception("TTS Error")
    success = test_voice.speak("Hello")
    assert not success

def test_voice_selection(test_voice, mock_pyttsx3):
    """Test Windows voice selection."""
    # Verify Zira voice was selected
    calls = mock_pyttsx3.setProperty.call_args_list
    voice_calls = [call for call in calls if call[0][0] == 'voice']
    assert any('zira' in str(call[0][1]).lower() for call in voice_calls)

def test_speech_rate_setting(test_voice):
    """Test speech rate adjustment."""
    success = test_voice.set_speech_rate(200)
    assert success
    assert test_voice.config.config['speech_rate'] == 200

def test_volume_setting(test_voice):
    """Test volume adjustment."""
    success = test_voice.set_volume(0.5)
    assert success
    assert test_voice.config.config['volume'] == 0.5

def test_vad_integration(test_voice, mock_vad):
    """Test Voice Activity Detection integration."""
    success, _ = test_voice._record_audio()
    assert success
    assert mock_vad.is_speech.called

def test_audio_saving(test_voice, tmp_path):
    """Test audio file saving functionality."""
    test_voice.audio_dir = tmp_path
    success, path = test_voice._record_audio()
    assert success
    assert Path(path).exists()
    
    # Verify wave file format
    with wave.open(path, 'rb') as wf:
        assert wf.getnchannels() == 1
        assert wf.getframerate() == 16000

def test_whisper_initialization(test_voice, mock_whisper):
    """Test Whisper model initialization."""
    assert hasattr(test_voice, 'whisper')
    mock_whisper.assert_called_once()

def test_config_persistence(test_voice, tmp_path):
    """Test configuration persistence."""
    test_voice.set_speech_rate(180)
    test_voice.set_volume(0.7)
    
    # Create new instance
    VoiceInterface._instance = None
    new_voice = get_voice_interface()
    
    assert new_voice.config.config['speech_rate'] == 180
    assert new_voice.config.config['volume'] == 0.7

def test_cleanup(test_voice, mock_pyaudio, mock_pyttsx3):
    """Test resource cleanup."""
    test_voice.__del__()
    assert mock_pyaudio.terminate.called
    assert mock_pyttsx3.stop.called

@pytest.mark.asyncio
async def test_retry_mechanism(test_voice, mock_whisper):
    """Test recognition retry mechanism."""
    # Make first attempt fail
    mock_whisper.transcribe.side_effect = [
        ([], None),  # First attempt - no transcription
        (MOCK_TRANSCRIPTION, None)  # Second attempt - success
    ]
    
    text = await test_voice.listen(max_retries=2)
    assert text == "Hello Zara"
    assert mock_whisper.transcribe.call_count == 2

def test_error_logging(test_voice, caplog):
    """Test error logging in voice operations."""
    with patch.object(test_voice.tts_engine, 'say', side_effect=Exception("TTS Error")):
        test_voice.speak("Test")
        assert "TTS Error" in caplog.text