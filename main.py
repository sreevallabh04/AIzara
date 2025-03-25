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
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
newsapi_key = "5d7bb59ceb154f1ead9161942835845e"  # NewsAPI key
weather_api_key = "029fd7af99a54f22ac6173050240108"  # Replace with your actual Weather API key
groq_api_key = os.getenv("GROQ_API_KEY")  # Get Groq API key from environment variable

# Initialize Groq client
groq_client = groq.Client(api_key=groq_api_key)

# Initialize TTS and STT engines
listener = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty('voice', engine.getProperty('voices')[1].id)  # Use a female voice
engine.setProperty('rate', 140)

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
    """Get a response from Groq AI for complex queries."""
    try:
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are Zara, a helpful virtual assistant. Provide concise, accurate responses."},
                {"role": "user", "content": query}
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error with Groq API: {e}")
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

def open_file(file_path):
    """Open a file using the default application with enhanced search capabilities."""
    try:
        # Convert file_path to lowercase for case-insensitive matching
        file_path_lower = file_path.lower()
        
        # Handle common locations with priorities
        common_locations = {
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
            "music": os.path.join(os.path.expanduser("~"), "Music"),
            "videos": os.path.join(os.path.expanduser("~"), "Videos")
        }
        
        # If no specific location was mentioned, these are the locations to search in priority order
        default_search_locations = [
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads"),
            os.getcwd()
        ]
        
        # Check if the path starts with a common location (case-insensitive)
        search_directories = []
        base_filename = file_path
        location_specified = False
        
        for location_name, location_path in common_locations.items():
            if file_path_lower.startswith(location_name.lower()):
                location_specified = True
                # Use the original case for removing the location prefix
                location_index = file_path_lower.find(location_name.lower())
                location_len = len(location_name)
                base_filename = file_path[location_index + location_len:].strip()
                search_directories.append(location_path)
                break
        
        # If no common location was found in the command
        if not location_specified:
            if os.path.dirname(file_path):
                # If path contains a directory separator
                search_directories.append(os.path.dirname(file_path))
                base_filename = os.path.basename(file_path)
            else:
                # No location specified, search in all default locations
                search_directories = default_search_locations
                base_filename = file_path
        
        # Remove extension if present for searching
        name_without_ext = os.path.splitext(base_filename)[0].strip()
        if not name_without_ext:  # If empty after stripping
            talk("Please specify a valid filename.")
            return False
            
        # Class to store file match information for sorting
        class FileMatch:
            def __init__(self, filename, path, score, mod_time):
                self.filename = filename
                self.full_path = path
                self.score = score  # Higher is better match
                self.mod_time = mod_time
                
            def __lt__(self, other):
                # First sort by score (descending), then by modification time (descending)
                if self.score != other.score:
                    return self.score > other.score
                return self.mod_time > other.mod_time
        
        # Collect all potential matches across all search directories
        all_matches = []
        
        for search_dir in search_directories:
            # First try the exact file path
            full_path = os.path.join(search_dir, base_filename)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                mod_time = os.path.getmtime(full_path)
                # Exact match with extension gets highest score
                all_matches.append(FileMatch(os.path.basename(full_path), full_path, 100, mod_time))
                continue  # Skip to next directory if exact match found
            
            # Function to recursively search for files
            def search_directory(directory, depth=0, max_depth=2):
                if depth > max_depth:
                    return  # Limit recursion depth
                
                try:
                    for item in os.listdir(directory):
                        item_path = os.path.join(directory, item)
                        
                        # Skip hidden files/folders
                        if item.startswith('.'):
                            continue
                            
                        # If it's a file, check for matches
                        if os.path.isfile(item_path):
                            item_lower = item.lower()
                            name_without_ext_lower = name_without_ext.lower()
                            item_name_without_ext = os.path.splitext(item)[0].lower()
                            
                            # Calculate match score based on various criteria
                            score = 0
                            
                            # Exact match without extension
                            if item_name_without_ext == name_without_ext_lower:
                                score = 90
                            # Item contains the search term as a whole word
                            elif name_without_ext_lower in item_name_without_ext.split():
                                score = 75
                            # Item filename starts with the search term
                            elif item_name_without_ext.startswith(name_without_ext_lower):
                                score = 60
                            # Item filename ends with the search term
                            elif item_name_without_ext.endswith(name_without_ext_lower):
                                score = 50
                            # Search term is contained within the item filename
                            elif name_without_ext_lower in item_name_without_ext:
                                score = 40
                            # Words in search term appear in filename (for multi-word searches)
                            elif any(word in item_name_without_ext for word in name_without_ext_lower.split()):
                                score = 30
                                
                            # If we have any score, it's a match
                            if score > 0:
                                mod_time = os.path.getmtime(item_path)
                                all_matches.append(FileMatch(item, item_path, score, mod_time))
                        
                        # If it's a directory, recurse into it if we haven't reached max depth
                        elif os.path.isdir(item_path) and depth < max_depth:
                            search_directory(item_path, depth + 1, max_depth)
                except (PermissionError, FileNotFoundError):
                    # Skip directories we can't access
                    pass
            
            # Perform the recursive search
            search_directory(search_dir)
        
        # Sort matches by score and recency
        all_matches.sort()
        
        # If we found matches, open the best one
        if all_matches:
            best_match = all_matches[0]
            talk(f"Opening {best_match.filename}")
            os.startfile(best_match.full_path)
            return True
        else:
            # If no location was specified, be generic in the error message
            if not location_specified:
                talk(f"I couldn't find any file matching '{name_without_ext}' in your common folders.")
            else:
                talk(f"I couldn't find any file matching '{name_without_ext}' in {os.path.basename(search_directories[0])}.")
            return False
    except Exception as e:
        talk(f"Error opening file: {str(e)}")
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
    else:
        # For complex or unrecognized commands, use AI
        response = get_ai_response(command)
        talk(response)
        print(response)
    return True

def run_zara():
    """Main loop to run the assistant."""
    talk("Hello, I am Zara, your virtual assistant. Now with enhanced AI capabilities. How can I help you today?")
    print("Hello, I am Zara, your virtual assistant. Now with enhanced AI capabilities. How can I help you today?")
    while True:
        command = take_command()
        if not execute_command(command):
            break

if __name__ == "__main__":
    run_zara()

