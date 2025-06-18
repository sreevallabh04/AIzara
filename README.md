# Zara Assistant 🎙️

An offline-first voice assistant powered by local LLMs, designed for privacy and performance. Think JARVIS, but running entirely on your machine!

## ✨ Features

- 🗣️ **Natural Voice Interface**
  - Speech recognition using Whisper (offline)
  - High-quality Windows TTS with configurable voices
  - Voice Activity Detection for better interaction

- 🧠 **Local Intelligence**
  - Powered by Ollama + LLaMA 2
  - Runs completely offline
  - Contextual memory and learning
  - Witty personality with natural responses

- 👁️ **Computer Vision**
  - Object detection using MobileNetSSD
  - Text recognition in images
  - Face detection
  - Screenshot analysis

- 🛠️ **System Integration**
  - Email and WhatsApp messaging
  - File operations
  - System commands
  - Web search capabilities

- 💾 **Persistent Memory**
  - Conversation history
  - User preferences
  - Task management
  - Automatic backups

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **Ollama** - [Download Ollama](https://ollama.ai/download)
3. **Git** (optional) - [Download Git](https://git-scm.com/downloads)

### Installation

1. Install Zara Assistant:
   ```bash
   pip install zara-assistant
   ```

   Or install from source:
   ```bash
   git clone https://github.com/yourusername/zara-assistant
   cd zara-assistant
   pip install -e .
   ```

2. Download the LLaMA model:
   ```bash
   ollama pull llama2
   ```

3. Start Ollama service:
   ```bash
   ollama serve
   ```

### Running Zara

1. Start the assistant:
   ```bash
   zara-assistant
   ```
   
   Or if installed from source:
   ```bash
   python -m zara
   ```

2. On first run, Zara will:
   - Check for Ollama service
   - Verify LLaMA model
   - Create necessary directories
   - Set up the database
   - Guide you through voice setup

## 🎯 Usage

### Voice Commands

Just speak naturally! Some examples:
- "What's the weather like?"
- "Send an email to John"
- "Take a screenshot"
- "What objects do you see in this image?"
- "Remember that I prefer dark mode"

### Configuration

Voice settings can be adjusted in `config/voice_config.json`:
```json
{
  "speech_rate": 175,
  "volume": 1.0,
  "vad_mode": 3,
  "input_timeout": 5.0
}
```

## 🛠️ Development

### Setting Up Dev Environment

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. Install dev dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov
   ```

### Running Tests

```bash
pytest tests/ -v
```

### Building Windows Executable

```bash
./build.bat
```

The executable will be created in `dist/Zara Assistant/`.

## 🔧 Troubleshooting

### Common Issues

1. **"Ollama service not detected"**
   - Ensure Ollama is installed
   - Run `ollama serve`
   - Check if http://localhost:11434 is accessible

2. **"LLaMA model not found"**
   - Run `ollama pull llama2`
   - Check available models with `ollama list`

3. **"No audio input detected"**
   - Check microphone permissions
   - Verify default input device
   - Adjust input volume

4. **"Vision model files missing"**
   - Ensure MobileNetSSD files are in the models directory
   - Download missing files if needed

### Logs

Check `logs/zara.log` for detailed error messages and debugging information.

## 📚 Architecture

Zara is built with modularity in mind:

```
zara/
├── agent.py      # Core LLM integration
├── memory.py     # Database and context
├── voice.py      # Speech I/O
├── vision.py     # Image processing
├── tools.py      # System operations
└── logger.py     # Logging system
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new features
4. Ensure tests pass
5. Create a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM support
- [Whisper](https://github.com/openai/whisper) for offline speech recognition
- [MobileNetSSD](https://github.com/chuanqi305/MobileNet-SSD) for vision capabilities