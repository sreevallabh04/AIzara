# Zara - AI-Powered Virtual Assistant

Zara is a Python-based virtual assistant similar to Amazon's Alexa, designed to perform a variety of tasks through voice commands. With the integration of Groq's advanced large language model, Zara now offers more sophisticated and natural conversational abilities.

## Features

- **Voice Recognition**: Listen and respond to voice commands
- **AI-Powered Responses**: Leverages Groq AI for complex queries and natural conversation
- **Weather Information**: Get current weather for any city
- **News Updates**: Read the latest news headlines
- **Wikipedia Access**: Fetch information from Wikipedia
- **YouTube Integration**: Play songs and videos on YouTube
- **Time and Date**: Tell the current time, date, and day
- **Web Search**: Perform Google searches and return top results
- **Web Navigation**: Open websites in your browser
- **File Access**: Open files on your computer using voice commands
- **Jokes**: Tell jokes when you need a laugh

## Prerequisites

- Python 3.7 or higher
- A Groq API key (for AI-powered responses)
- An internet connection for API services

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd zara-assistant
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your API keys:
```
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

Run the assistant with:
```
python main.py
```

### Voice Commands

Activate Zara by saying "Zara" followed by a command:

- "Zara, what time is it?"
- "Zara, what's the weather in London?"
- "Zara, play Bohemian Rhapsody"
- "Zara, tell me about Albert Einstein"
- "Zara, tell me a joke"
- "Zara, search for pasta recipes"
- "Zara, open youtube"
- "Zara, open file Documents report.docx"
- "Zara, open Desktop presentation.pptx"
- "Zara, what's the news today?"
- "Zara, explain quantum computing" (uses Groq AI)
- "Zara, what is the meaning of life?" (uses Groq AI)

For complex questions or general conversation, Zara will automatically use the Groq API to provide intelligent responses.

## Configuration

You can customize Zara by modifying the parameters in `main.py`:

- Change the voice by modifying the voice property
- Adjust the speech rate
- Add or modify commands in the `execute_command` function

## Opening Files and Websites

Zara can intelligently determine whether you want to open a file or a website:

### How Zara Decides Between Files and Websites

When you say "Zara, open something", Zara uses the following decision process:

1. **Explicit Commands** (most certain):
   - If you say "open file resume" → Zara treats it as a file
   - If you say "open website facebook" → Zara treats it as a website

2. **Path Detection** (very certain):
   - If it's an existing file path → Zara opens it as a file
   - If it contains path separators (\ or /) → Zara searches for it as a file

3. **Location Detection** (very certain):
   - If it starts with a common location (Desktop, Documents, etc.) → Zara searches for it as a file

4. **Website Recognition** (very certain):
   - If it contains web indicators (.com, www., http:, etc.) → Zara opens it as a website
   - If it's a common website name (google, youtube, facebook, etc.) → Zara opens it as a website

5. **Ambiguous Cases** (least certain):
   - For anything else, Zara will:
     - First try to find it as a file in common locations
     - If no file is found, open it as a website (adding .com)

Zara always tells you what it's doing with feedback like "Looking for file..." or "Opening website..."

### File Opening Functionality

- **Common Locations**: Say "open file [location] [filename]" where location can be:
  - Documents
  - Downloads
  - Desktop
  - Pictures
  - Music
  - Videos

- **Direct Paths**: Say "open [full path]" for files anywhere on your system:
  - "Zara, open C:\Users\username\Documents\report.pdf"

- **No Extension Required**: You don't need to specify file extensions:
  - Simply say "Zara, open Desktop resume" to open resume.docx or any file named resume with any extension
  - The assistant will automatically find the matching file regardless of its extension

- **Case-Insensitive Search**: File searching is completely case-insensitive:
  - Commands like "Zara, open DESKTOP Resume" or "Zara, open desktop RESUME" all work the same
  - Location names and filenames are matched regardless of capitalization

- **Fuzzy Name Matching**: Zara can find files that partially match what you said:
  - If you say "Zara, open resume" and have a file named "resume_2023.docx", Zara will find it

- **Smart Multi-Location Search**: 
  - Simply say "Zara, open resume" without specifying location
  - Zara will search Desktop, Documents, Downloads, and current directory automatically
  - No need to remember where you stored a file

- **Recursive Search**:
  - Zara searches in subdirectories, not just the top level
  - Files in nested folders will be found automatically

- **Intelligent Prioritization**:
  - When multiple matching files exist, Zara prioritizes by relevance score and recency
  - Most recently modified files that closely match your request are opened first

## Groq AI Integration

The integration with Groq's LLM provides Zara with advanced capabilities:

- More natural and contextual conversations
- Ability to answer complex questions
- Explaining complicated topics
- General knowledge beyond the built-in capabilities

The assistant will automatically use Groq AI when:
- A question starts with "ask," "answer," or "explain"
- The command doesn't match any of the predefined command patterns

## Troubleshooting

- If voice recognition isn't working, check your microphone settings
- Ensure all API keys are correctly set in the `.env` file
- For issues with Groq API responses, verify your API key and internet connection

## License

This project is licensed under the MIT License - see the LICENSE file for details.