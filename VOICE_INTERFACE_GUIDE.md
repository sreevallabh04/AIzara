# Zara Assistant - Enhanced Voice Interface Guide

## 🎤 New Conversational Voice Interface

Zara now has a much more natural and conversational voice interface with wake word detection and seamless email automation!

## ✨ Key Features

### 🔥 Wake Word Detection
- **Say "Zara"** to get her attention
- **Natural variations supported**: "Sarah", "Sara", "Clara", "Zahra" (for speech recognition errors)
- **Direct commands**: "Zara send email to Amma" (processes immediately)
- **Conversation mode**: Just say "Zara" to start a conversation

### 💬 Natural Conversation Flow
- **Context awareness**: Remembers what you talked about
- **Conversational responses**: Feels like talking to a real assistant
- **Error handling**: Clear feedback when something doesn't work
- **Personality**: Zara has a friendly, helpful personality

### 📧 Contact-Based Email Automation
- **By name**: "Zara send email to Amma" → automatically uses sudharanivaidya@gmail.com
- **With context**: "Zara email Shivani about dinner saying let's meet at 7"
- **Subject extraction**: "about dinner" becomes the email subject
- **Message extraction**: "saying let's meet at 7" becomes the email body

## 🎯 How to Use

### Starting Zara
```bash
python run_zara_voice.py
```

### Wake Word Commands

#### Basic Wake Word
```
You: "Zara"
Zara: "Hello! I'm Zara, your personal assistant. How can I help you today?"
You: "Send an email to Amma"
Zara: [Opens Gmail with Amma's email pre-filled]
```

#### Direct Commands
```
You: "Zara send email to Shivani about project update"
Zara: [Immediately opens Gmail with email to Shivani, subject "project update"]
```

#### Advanced Commands
```
You: "Zara email Hansika about meeting saying we should discuss the budget tomorrow"
Zara: [Opens Gmail with:
  - To: kallurihansikareddy5@gmail.com
  - Subject: meeting
  - Body: we should discuss the budget tomorrow]
```

## 📱 Supported Voice Commands

### Email Commands
| Command | Action |
|---------|--------|
| `Zara send email to [name]` | Opens Gmail to compose email to contact |
| `Zara email [name] about [subject]` | Pre-fills subject line |
| `Zara email [name] saying [message]` | Pre-fills message body |
| `Zara compose email to [name] about [subject] saying [message]` | Complete email automation |

### Contact Commands
| Command | Action |
|---------|--------|
| `Zara show contacts` | Lists all your contacts |
| `Zara find contact [name]` | Shows specific contact info |
| `Zara add contact [name]` | Adds new contact (interactive) |

### Conversation Commands
| Command | Action |
|---------|--------|
| `Zara` | Starts conversation mode |
| `Hello` / `Hi` | Greeting responses |
| `Goodbye` / `Bye` | Ends conversation |

## 🎨 Conversation Examples

### Natural Email Flow
```
You: "Zara"
Zara: "Hi there! Zara here, ready to assist you. What can I do for you?"
You: "I need to email my mom about dinner plans"
Zara: "I'm on it! Opening Gmail with an email to Amma about dinner plans."
[Gmail opens with sudharanivaidya@gmail.com, subject: "dinner plans"]
```

### Quick Commands
```
You: "Zara email Raazi saying thanks for the help"
Zara: "Right away! Gmail is now open with your email pre-filled for Raazi."
[Gmail opens with raazi.faisal@gmail.com, message: "thanks for the help"]
```

### Error Handling
```
You: "Zara send email to unknown person"
Zara: "I couldn't find 'unknown person' in your address book. Would you like me to show your contacts?"
```

## 🔧 Technical Features

### Voice Recognition
- **Model**: Whisper (base) for accurate speech-to-text
- **Languages**: Optimized for English
- **Noise handling**: Works in normal room environments
- **Duration**: 3-8 second recording windows

### Audio Configuration
- **Sample Rate**: 16kHz
- **Format**: 16-bit PCM
- **Channels**: Mono
- **Auto-device selection**: Finds best microphone automatically

### Response Generation
- **AI Engine**: LLaMA 3.2 via Ollama
- **Context**: Remembers last 5 interactions
- **Tool Integration**: Automatic email, contacts, web search
- **Personality**: Consistent friendly assistant character

## 🛠️ Setup & Configuration

### Requirements
```bash
pip install -r requirements.txt
```

### Voice Configuration
Edit `config/voice_config.json`:
```json
{
    "speech_rate": 175,
    "volume": 0.9,
    "recording_duration": 5.0,
    "wake_word_timeout": 30.0,
    "conversation_timeout": 180.0
}
```

### Your Contacts
Your contacts are already set up:
- **Amma**: sudharanivaidya@gmail.com
- **Shivani**: dathashivani09@gmail.com
- **Sahith**: sahithraolingampally@gmail.com
- **Raazi**: raazi.faisal@gmail.com
- **Hansika**: kallurihansikareddy5@gmail.com
- **Soham**: sohamshashidhar@gmail.com
- **Shahzil**: theshahzil@gmail.com

## 🎯 Best Practices

### For Best Voice Recognition
1. **Speak clearly** and at normal pace
2. **Wait for the beep** before speaking
3. **Use natural language** - no need for robotic commands
4. **Say "Zara" clearly** to wake her up

### For Email Commands
1. **Use contact names** exactly as stored (Amma, not Mom)
2. **Be specific** about subjects: "about project" not just "project"
3. **Natural phrasing**: "saying hello" instead of "message hello"

### For Conversations
1. **Wait for Zara to finish** speaking before responding
2. **Say "goodbye"** to end conversations cleanly
3. **Use clarification** if something doesn't work: "Try again"

## 🚀 Quick Start

1. **Start Zara**: `python run_zara_voice.py`
2. **Test wake word**: Say "Zara"
3. **Try email**: "Send email to Amma"
4. **Check contacts**: "Show my contacts"
5. **End session**: "Goodbye"

## 🐛 Troubleshooting

### No Microphone Detected
- Check microphone connection
- Run audio test: `python -c "import pyaudio; print('Audio devices:', pyaudio.PyAudio().get_device_count())"`

### Wake Word Not Working
- Speak louder and clearer
- Try variations: "Sarah" instead of "Zara"
- Check if Whisper model is loaded

### Email Not Opening
- Check internet connection
- Verify Gmail account is logged in browser
- Check contact names with: `python setup_contacts.py`

### Voice Recognition Issues
- Reduce background noise
- Speak at normal pace
- Wait for recording prompt

## 💡 Pro Tips

1. **Batch commands**: "Zara email Amma about dinner, then show my contacts"
2. **Context switching**: Start conversations for complex tasks
3. **Name shortcuts**: Use short names like "Hansika" instead of full names
4. **Natural speech**: Talk like you would to a human assistant

---

🎉 **Enjoy your enhanced conversational experience with Zara!**

Your assistant is now much more natural, intelligent, and helpful. Just say "Zara" and start talking! 