# Zara - Futuristic AI-Powered Virtual Assistant

Zara is a next-generation, multimodal AI assistant that combines voice, vision, and language to help you in everyday life. Zara can see, hear, speak, read, translate, summarize, and even help with accessibility and sustainability—all through natural voice commands.

## 🚀 Features

### 🤖 Conversational AI
- Natural, context-aware conversation using Gemini AI (with memory of previous interactions)
- Moderated, safe, and friendly responses as "Zara"

### 🗣️ Voice Commands
- Activate Zara by saying "Zara" followed by your command
- Example: "Zara, what can you do?"

### 👁️ Live Camera Narration
- **Command:** `start live camera description`
- Shows a live camera feed and describes what Zara sees in real time (object detection)

### 📝 OCR & Translation
- **Command:** `read and translate text from camera to <language>`
- Reads text from the camera and translates it to any language (e.g., French, Hindi, Spanish)

### 📧 Email by Voice
- **Command:** `send email to <address> subject <subject> body <body>`
- If the body is omitted, Zara will write the email for you using AI

### 📂 Smart File Opening
- **Command:** `open file <filename>`
- Securely opens files from Desktop or Documents with fuzzy, case-insensitive matching

### 📅 Meeting Summarizer
- **Command:** `summarize meeting`
- Records, transcribes, and summarizes meetings or lectures

### 🔊 Environmental Sound Detection
- **Command:** `detect environmental sound`
- Listens for and identifies environmental sounds (stub for advanced sound classification)

### ✋ Gesture Recognition (Stub)
- **Command:** `recognize gesture`
- Placeholder for future gesture recognition using the camera

### ♻️ Waste Sorting Assistant (Stub)
- **Command:** `waste sorting assistant`
- Placeholder for future waste classification (recyclable, compost, trash)

### 🌐 Web & Knowledge
- Wikipedia summaries, Google search, news, weather, jokes, and more

### 🧑‍🦯 Accessibility
- Visual narration, text reading, and translation for the visually impaired

### 🛡️ Safety & Moderation
- Content moderation for safe, appropriate responses
- File and command validation for security

### 🗃️ Persistent Memory
- Conversation history and user data stored in a local SQLite database

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd AIzara
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables in a `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   EMAIL_ADDRESS=your_email_address_here
   EMAIL_PASSWORD=your_email_password_here
   ```
4. (Optional) For OCR, install Tesseract OCR engine and add it to your PATH.

## 🏁 Usage

Run Zara with:
```
python main.py
```

Then use any of the voice commands above!

## 🏆 Hackathon-Ready, Real-World Impact
- Accessibility for the visually impaired
- Productivity (meeting summarization, email, translation)
- Environmental awareness (waste sorting, sound detection)
- Extensible for smart home, AR, and more

## 📚 Extending Zara
- Add new skills by editing `main.py` and following the command pattern
- Integrate with APIs, IoT devices, or AR overlays for even more futuristic features

## 📝 License
MIT License