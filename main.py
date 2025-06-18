import asyncio
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes
import time
import webbrowser
import os
import requests
import aiohttp
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import google.generativeai as genai
from dotenv import load_dotenv
import sqlite3
import smtplib
from email.message import EmailMessage
import cv2
from PIL import Image
import io
import urllib.request
import numpy as np
import shutil
import pytesseract
from googletrans import Translator
import sounddevice as sd
import scipy.io.wavfile as wav
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess

# Load environment variables
load_dotenv()

# API Keys
newsapi_key = "5d7bb59ceb154f1ead9161942835845e"  # NewsAPI key
weather_api_key = "029fd7af99a54f22ac6173050240108"  # Replace with your actual Weather API key
gemini_api_key = os.getenv("GEMINI_API_KEY")  # Load Gemini API key from environment variable

# Initialize Gemini client
genai.configure(api_key=gemini_api_key)

# Initialize TTS and STT engines
listener = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[1].id)  # Use a female voice
engine.setProperty('rate', 140)

# Database setup
DB_PATH = 'zara_assistant.db'
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT,
        value TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Conversation memory helpers
def save_conversation(role, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO conversation_history (role, content) VALUES (?, ?)', (role, content))
    conn.commit()
    conn.close()

def load_recent_conversation(n=10):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?', (n,))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]  # Return in chronological order

# Moderation helper
def moderate_content(text):
    banned_words = ["badword1", "badword2"]
    for word in banned_words:
        if word in text.lower():
            return False
    return True

def talk(text):
    """Speak the given text aloud."""
    engine.say(text)
    engine.runAndWait()

def take_command(trigger_word_active=True):
    """Listen for a command and return it as text."""
    command = ""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source, duration=1)
            voice = listener.listen(source, timeout=10, phrase_time_limit=10)
            command = listener.recognize_google(voice).lower()
            if trigger_word_active and "zara" in command:
                command = command.replace("zara", "").strip()
            print(f"Command: {command}")
    except sr.UnknownValueError:
        print("Could not understand the audio.")
    except sr.RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return command
    
def get_ai_response(query):
    if not gemini_api_key:
        return "Gemini API key is not set. Please set the API key."
    try:
        # Persona system prompt
        system_prompt = {"role": "system", "content": "You are Zara, a helpful, safe, and conversational AI assistant. Always respond as Zara."}
        # Load last 10 exchanges
        history = load_recent_conversation(10)
        context = [system_prompt] + [{"role": r, "content": c} for r, c in history] + [{"role": "user", "content": query}]
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(context)
        save_conversation("user", query)
        save_conversation("assistant", response.text)
        return response.text
    except Exception as e:
        return "I'm having trouble connecting to my knowledge base right now."

def get_wikipedia_summary(query):
    """Get a summary from Wikipedia."""
    try:
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError:
        return "There are multiple entries for this topic. Please be more specific."
    except wikipedia.exceptions.PageError:
        return "Sorry, I couldn't find any information on that topic."
    except Exception as e:
        return f"Error retrieving information: {e}"

def search_google(query):
    """Perform a Google search and return the top links."""
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.google.com")
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(2)
    results = driver.find_elements(By.CSS_SELECTOR, 'h3')
    links = [result.find_element(By.XPATH, '..').get_attribute('href') for result in results[:5]]
    driver.quit()
    return links

async def get_weather(city_name):
    """Fetch weather data using Weather API."""
    base_url = "http://api.weatherapi.com/v1/current.json"
    url = f"{base_url}?key={weather_api_key}&q={city_name}&aqi=no"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                temperature = data['current']['temp_c']
                location = data['location']['name']
                talk(f"The temperature in {location} is {temperature} degrees Celsius.")
                return f"The temperature in {location} is {temperature}°C."
            else:
                return "Failed to fetch weather data."

def get_news():
    """Fetch the top news headlines."""
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi_key}"
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            headlines = [article["title"] for article in articles[:5]]
            talk("Here are the top news headlines.")
            for headline in headlines:
                talk(headline)
            return headlines
        else:
            return ["Failed to fetch news."]
    except Exception as e:
        return [f"Error fetching news: {e}"]

def is_safe_path(file_path):
    safe_dirs = [os.path.join(os.path.expanduser("~"), d) for d in ["Desktop", "Documents"]]
    abs_path = os.path.abspath(file_path)
    return any(abs_path.startswith(os.path.abspath(safe)) for safe in safe_dirs)

def open_file(file_path):
    # If file_path is a full path, open it directly
    if os.path.exists(file_path):
        talk(f"Opening {file_path} now.")
        os.startfile(file_path)
        return True
    # Otherwise, search the entire laptop for the file
    talk(f"Searching for {file_path}...")
    for root, dirs, files in os.walk(os.path.expanduser("~")):
        for file in files:
            if file.lower() == file_path.lower():
                full_path = os.path.join(root, file)
                talk(f"Found {file} at {full_path}. Opening now.")
                os.startfile(full_path)
                return True
    talk(f"Sorry, I couldn't find a file named {file_path}.")
    return False

def is_likely_website(text):
    """Determine if the text is likely a website name rather than a file."""
    # Common website indicators
    website_indicators = [
        ".com", ".org", ".net", ".edu", ".gov", ".io", ".co", 
        "www.", "http:", "https:", "website", "site"
    ]
    
    # Common website names that might not have extensions in commands
    common_websites = [
        "google", "youtube", "facebook", "twitter", "linkedin", "instagram",
        "amazon", "netflix", "github", "stackoverflow", "reddit", "wikipedia"
    ]
    
    # Check for website indicators
    text_lower = text.lower()
    if any(indicator in text_lower for indicator in website_indicators):
        return True
        
    # Check if it's a common website name
    if any(site == text_lower or site in text_lower.split() for site in common_websites):
        return True
        
    # Check if it looks like a domain (single word without spaces, dots, or special chars)
    if (" " not in text and 
        "." not in text and 
        "\\" not in text and 
        "/" not in text and 
        len(text) > 0 and 
        len(text) <= 20):
        return True
        
    return False

def capture_camera_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        # Convert frame to PIL Image
        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # Convert PIL Image to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr
    return None

def describe_camera_image():
    img_bytes = capture_camera_image()
    if img_bytes:
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(["Describe what you see in this image:", img_bytes])
            return response.text
        except Exception as e:
            return f"Error describing image: {e}"
    return "Failed to capture image from camera."

def ocr_and_translate_camera_text(target_lang='en'):
    img_bytes = capture_camera_image()
    if img_bytes:
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(image)
            if not text.strip():
                talk("I couldn't find any readable text in the camera view.")
                return
            talk(f"I see the following text: {text}")
            translator = Translator()
            translated = translator.translate(text, dest=target_lang)
            talk(f"Translated text: {translated.text}")
        except Exception as e:
            talk(f"Error reading or translating text: {e}")
    else:
        talk("Failed to capture image from camera.")

def execute_command(command):
    """Process and execute user commands."""
    if 'play' in command:
        song = command.replace('play', '').strip()
        talk(f"Playing {song}")
        pywhatkit.playonyt(song)
    elif 'time' in command:
        time_now = datetime.datetime.now().strftime('%I:%M %p')
        talk(f"The current time is {time_now}")
    elif 'date' in command:
        date_today = datetime.datetime.now().strftime('%d %B, %Y')
        talk(f"Today's date is {date_today}")
    elif 'day' in command:
        day_today = datetime.datetime.now().strftime('%A')
        talk(f"Today is {day_today}")
    elif 'weather in' in command:
        city = command.replace('weather in', '').strip()
        asyncio.run(get_weather(city))
    elif 'news' in command:
        headlines = get_news()
        for headline in headlines:
            print(headline)
    elif 'who is' in command or 'tell me about' in command:
        topic = command.replace('who is', '').replace('tell me about', '').strip()
        summary = get_wikipedia_summary(topic)
        talk(summary)
    elif 'joke' in command:
        joke = pyjokes.get_joke()
        talk(joke)
    elif 'search' in command:
        query = command.replace('search', '').strip()
        talk("Searching Google...")
        links = search_google(query)
        for link in links:
            print(link)
    # Explicit file opening command
    elif 'open file' in command:
        file_path = command.replace('open file', '').strip()
        talk(f"Looking for file: {file_path}")
        open_file(file_path)
    # Explicit website opening command
    elif 'open website' in command or 'open site' in command:
        site = command.replace('open website', '').replace('open site', '').strip()
        talk(f"Opening {site} website")
        if not site.startswith('http'):
            if '.' not in site:
                site = f"{site}.com"
            site = f"https://{site}"
        webbrowser.open(site)
    # General open command - need to determine if file or website
    elif 'open' in command:
        target = command.replace('open', '').strip()
        
        # Decision process for file vs website (in order of certainty)
        
        # 1. Check if it's an exact existing path
        if os.path.exists(target):
            talk(f"Opening file: {os.path.basename(target)}")
            open_file(target)
            
        # 2. Check if it has file path separators
        elif '\\' in target or '/' in target:
            talk(f"Looking for file: {target}")
            open_file(target)
            
        # 3. Check if it starts with a known location
        elif any(target.lower().startswith(loc.lower()) for loc in ["desktop", "documents", "downloads", 
                                                                  "pictures", "music", "videos"]):
            talk(f"Looking for file in {target.split()[0]}")
            open_file(target)
            
        # 4. Check if it looks like a website
        elif is_likely_website(target):
            talk(f"Opening {target} website")
            if not target.startswith('http'):
                if '.' not in target:
                    target = f"{target}.com"
                target = f"https://{target}"
            webbrowser.open(target)
            
        # 5. If ambiguous, try as file first, then website if not found
        else:
            talk(f"Looking for file named: {target}")
            if not open_file(target):
                talk(f"File not found. Opening {target} website instead")
                if '.' not in target:
                    target = f"{target}.com"
                webbrowser.open(f"https://{target}")
    elif 'exit' in command or 'bye' in command:
        talk("Goodbye! Have a great day!")
        return False
    elif 'ask' in command or 'answer' in command or 'explain' in command:
        query = command.replace('ask', '').replace('answer', '').replace('explain', '').strip()
        talk("Let me think about that...")
        response = get_ai_response(query)
        talk(response)
        print(response)
    elif command.startswith("what can you do"):
        features = [
            "I can tell you the time and date.",
            "I can fetch the weather for any city.",
            "I can read the latest news headlines.",
            "I can search and summarize Wikipedia topics.",
            "I can play songs and videos on YouTube.",
            "I can perform Google searches and return top results.",
            "I can open websites and files on your computer.",
            "I can tell jokes.",
            "I can answer complex questions using Gemini AI."
        ]
        talk("Here are some things I can do:")
        for feature in features:
            talk(feature)
        return True
    elif command.startswith("send email"):
        try:
            parts = command.split(" ")
            to_idx = parts.index("to") + 1
            subject_idx = parts.index("subject") + 1
            body_idx = parts.index("body") + 1
            to_address = parts[to_idx]
            subject = " ".join(parts[subject_idx:body_idx-1])
            body = " ".join(parts[body_idx:])
            # For demo: get sender email/password from environment or prompt
            from_address = os.getenv("EMAIL_ADDRESS")
            from_password = os.getenv("EMAIL_PASSWORD")
            if not from_address or not from_password:
                talk("Email credentials are not set. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in your environment.")
                return False
            send_email(to_address, subject, body, from_address, from_password)
            return True
        except Exception as e:
            talk(f"Failed to parse email command: {e}")
            return False
    elif command.startswith("describe camera"):
        description = describe_camera_image()
        talk(description)
        return True
    elif command.startswith("start live camera description"):
        live_camera_description()
        return True
    elif command.startswith("read and translate text from camera"):
        # Parse target language if specified
        target_lang = 'en'
        if 'to ' in command:
            target_lang = command.split('to ')[-1].strip()
        ocr_and_translate_camera_text(target_lang)
        return True
    elif command.startswith("summarize meeting"):
        record_and_summarize_meeting()
        return True
    elif command.startswith("detect environmental sound"):
        detect_environmental_sound()
        return True
    elif command.startswith("recognize gesture"):
        recognize_gesture()
        return True
    elif command.startswith("waste sorting assistant"):
        waste_sorting_assistant()
        return True
    elif command.startswith("open whatsapp"):
        open_app("WhatsApp")
        return True
    elif command.startswith("send whatsapp message to"):
        try:
            open_app("WhatsApp")
            time.sleep(5)  # Give WhatsApp time to open
            parts = command.split("message")
            contact = parts[0].replace("send whatsapp message to", "").strip()
            message = parts[1].strip()
            # Optionally, automate typing using pyautogui here
            talk("Please select the contact and I will type the message.")
            # You can add pyautogui.typewrite(message) for full automation
            return True
        except Exception as e:
            talk(f"Failed to parse WhatsApp command: {e}")
            return False
    else:
        # For complex or unrecognized commands, use AI
        response = get_ai_response(command)
        talk(response)
        print(response)
    return True

def run_zara():
    """Run the Zara assistant in a production-ready loop."""
    talk("Hello! I am Zara, your virtual assistant. How can I help you today?")
    while True:
        try:
            command = take_command()
            if command:
                execute_command(command)
        except Exception as e:
            print(f"Error in run_zara: {e}")
            talk("I encountered an error. Please try again.")

def send_email(to_address, subject, body, from_address, from_password, smtp_server='smtp.gmail.com', smtp_port=587):
    try:
        if not body:
            # Use Gemini AI to generate email body if empty
            prompt = f"Write a professional email with subject: {subject} to {to_address}."
            body = get_ai_response(prompt)
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = to_address
        msg.set_content(body)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_address, from_password)
            server.send_message(msg)
        talk("Email sent successfully.")
        return True
    except Exception as e:
        talk(f"Failed to send email: {e}")
        return False

# Download MobileNet-SSD model files if not present
def download_mobilenet_ssd():
    proto_url = 'https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.prototxt'
    model_url = 'https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel'
    proto_file = 'MobileNetSSD_deploy.prototxt'
    model_file = 'MobileNetSSD_deploy.caffemodel'
    def download_file(url, file):
        try:
            urllib.request.urlretrieve(url, file)
            return True
        except Exception as e:
            if os.path.exists(file):
                os.remove(file)
            print(f"Failed to download {file}: {e}")
            return False
    # Check and download prototxt
    if not os.path.exists(proto_file) or os.path.getsize(proto_file) < 1000:
        if os.path.exists(proto_file):
            os.remove(proto_file)
        print(f"Downloading {proto_file}...")
        if not download_file(proto_url, proto_file):
            raise RuntimeError(f"Could not download {proto_file}. Please download it manually from {proto_url} and place it in the project directory.")
    # Check and download caffemodel
    if not os.path.exists(model_file) or os.path.getsize(model_file) < 100000:
        if os.path.exists(model_file):
            os.remove(model_file)
        print(f"Downloading {model_file}...")
        if not download_file(model_url, model_file):
            raise RuntimeError(f"Could not download {model_file}. Please download it manually from {model_url} and place it in the project directory.")
    return proto_file, model_file

# Object classes for MobileNet-SSD
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant",
           "sheep", "sofa", "train", "tvmonitor"]

def detect_objects_mobilenet(frame, net):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    detected = set()
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            idx = int(detections[0, 0, i, 1])
            if idx < len(CLASSES):
                detected.add(CLASSES[idx])
    return detected

def live_camera_description():
    proto_file, model_file = download_mobilenet_ssd()
    net = cv2.dnn.readNetFromCaffe(proto_file, model_file)
    cap = cv2.VideoCapture(0)
    last_objects = set()
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        objects = detect_objects_mobilenet(frame, net)
        if objects != last_objects:
            if objects:
                desc = ", ".join(objects)
                talk(f"Zara sees: {desc}")
            else:
                talk("Zara doesn't see anything recognizable.")
            last_objects = objects
        cv2.imshow('Zara Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Meeting summarization: record, transcribe, summarize
def record_and_summarize_meeting(duration=30):
    talk("Recording meeting audio now.")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio = recognizer.listen(source, phrase_time_limit=duration)
    try:
        text = recognizer.recognize_google(audio)
        talk("Transcribing and summarizing the meeting.")
        summary = get_ai_response(f"Summarize this meeting transcript: {text}")
        talk(f"Meeting summary: {summary}")
    except Exception as e:
        talk(f"Error transcribing or summarizing: {e}")

# Environmental sound detection (stub)
def detect_environmental_sound(duration=5):
    talk("Listening for environmental sounds.")
    fs = 44100
    try:
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        # For demo, just say we heard something
        talk("I heard a sound. (Advanced sound classification can be added here.)")
    except Exception as e:
        talk(f"Error detecting sound: {e}")

# Gesture recognition stub
def recognize_gesture():
    talk("Gesture recognition is not yet implemented, but this is where it would go.")

# Waste sorting assistant stub
def waste_sorting_assistant():
    talk("Waste sorting is not yet implemented, but this is where it would go. Show an object to the camera and Zara will classify it as recyclable, compost, or trash in the future.")

def open_app(app_name):
    if app_name.lower() == "whatsapp":
        try:
            webbrowser.open('https://web.whatsapp.com')
            talk("Opening WhatsApp web now.")
            return True
        except Exception as e:
            talk(f"Failed to open WhatsApp web: {e}")
            return False
    else:
        try:
            subprocess.Popen(['powershell', 'Start-Process', app_name])
            talk(f"Opening {app_name} now.")
            return True
        except Exception as e:
            talk(f"Failed to open {app_name}: {e}")
            return False

if __name__ == "__main__":
    run_zara()

