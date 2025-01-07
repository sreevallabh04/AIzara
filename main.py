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

# API Keys
newsapi_key = "e1b9396392044aa5bcecb7f0ab29dbb6"  # Replace with your actual News API key
weather_api_key = "029fd7af99a54f22ac6173050240108"  # Replace with your actual Weather API key

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
    elif 'open' in command:
        site = command.replace('open', '').strip()
        talk(f"Opening {site}")
        webbrowser.open(f"https://{site}.com")
    elif 'exit' in command or 'bye' in command:
        talk("Goodbye! Have a great day!")
        return False
    else:
        talk("Sorry, I didn't understand that.")
    return True

def run_zara():
    """Main loop to run the assistant."""
    talk("Hello, I am Zara, your virtual assistant. How can I help you today?")
    print("Hello, I am Zara, your virtual assistant. How can I help you today?")
    while True:
        command = take_command()
        if not execute_command(command):
            break

if __name__ == "__main__":
    run_zara()

