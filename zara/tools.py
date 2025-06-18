import os
import subprocess
import json
import cv2
import numpy as np
from datetime import datetime
import pyautogui
import pygetwindow as gw
import webbrowser
import time
import psutil
import win32gui
import win32con
import win32process
import win32api

def find_window_by_title(title):
    """Find a window by its title."""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title.lower() in window_title.lower():
                windows.append(hwnd)
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None

def activate_window(hwnd):
    """Activate a window by its handle."""
    try:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False

def send_whatsapp_message(contact, message):
    """Send a WhatsApp message to a contact."""
    try:
        # First ensure WhatsApp is open
        open_whatsapp_desktop()
        time.sleep(2)  # Wait for WhatsApp to load
        
        # Find and activate WhatsApp window
        hwnd = find_window_by_title("WhatsApp")
        if not hwnd:
            return "Error: Could not find WhatsApp window"
        
        if not activate_window(hwnd):
            return "Error: Could not activate WhatsApp window"
        
        # Search for contact
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        pyautogui.write(contact)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        
        # Type and send message
        pyautogui.write(message)
        pyautogui.press('enter')
        
        return f"Message sent to {contact}: {message}"
    except Exception as e:
        return f"Error sending WhatsApp message: {str(e)}"

def open_whatsapp_desktop():
    """Open the WhatsApp desktop application."""
    try:
        # Try to find existing WhatsApp window
        hwnd = find_window_by_title("WhatsApp")
        if hwnd:
            if activate_window(hwnd):
                return "WhatsApp window activated"
        
        # If not found, launch WhatsApp
        subprocess.Popen(["start", "whatsapp:"], shell=True)
        time.sleep(2)  # Wait for WhatsApp to start
        
        # Try to find and activate the window again
        hwnd = find_window_by_title("WhatsApp")
        if hwnd:
            if activate_window(hwnd):
                return "WhatsApp opened and activated"
        
        return "Opening WhatsApp desktop app"
    except Exception as e:
        return f"Error opening WhatsApp: {str(e)}"

def open_app(app_name):
    """Open any application on the computer."""
    try:
        # Handle special cases
        if app_name.lower() in ['chrome', 'google chrome']:
            subprocess.Popen(["start", "chrome"], shell=True)
        elif app_name.lower() in ['notepad', 'notepad++']:
            subprocess.Popen(["start", "notepad"], shell=True)
        else:
            # Try to open the app directly
            subprocess.Popen(["start", app_name], shell=True)
        
        # Wait for the app to start
        time.sleep(2)
        
        # Try to find and activate the window
        hwnd = find_window_by_title(app_name)
        if hwnd:
            if activate_window(hwnd):
                return f"{app_name} opened and activated"
        
        return f"Opening {app_name}"
    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def capture_image():
    """Capture an image using the computer's camera."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Error: Could not open camera"
        
        # Wait for camera to initialize
        time.sleep(1)
        
        ret, frame = cap.read()
        if not ret:
            return "Error: Could not capture image"
        
        # Save the image with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = f"captured_image_{timestamp}.jpg"
        cv2.imwrite(image_path, frame)
        cap.release()
        
        return f"Image captured and saved as {image_path}"
    except Exception as e:
        return f"Error capturing image: {str(e)}"

def describe_image(image_path):
    """Describe an image using computer vision."""
    try:
        if not os.path.exists(image_path):
            return f"Error: Image file {image_path} not found"
        
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            return f"Error: Could not read image {image_path}"
        
        # TODO: Implement actual image description using a vision model
        return f"Image {image_path} loaded successfully. Description to be implemented."
    except Exception as e:
        return f"Error describing image: {str(e)}"

def search_google(query):
    """Search Google for information."""
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return f"Searching Google for: {query}"
    except Exception as e:
        return f"Error performing Google search: {str(e)}"

def open_file(file_path):
    """Open a file on the computer."""
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} not found"
        
        os.startfile(file_path)
        return f"Opening file: {file_path}"
    except Exception as e:
        return f"Error opening file: {str(e)}"

def play_music(source):
    """Play music from a specified source."""
    try:
        # Handle different music sources
        if source.lower() in ['spotify', 'spotify music']:
            subprocess.Popen(["start", "spotify:"], shell=True)
            return "Opening Spotify"
        elif source.lower() in ['youtube', 'youtube music']:
            webbrowser.open("https://music.youtube.com")
            return "Opening YouTube Music"
        else:
            # Try to open the source as a file or URL
            if os.path.exists(source):
                os.startfile(source)
                return f"Playing music from: {source}"
            else:
                webbrowser.open(source)
                return f"Opening music source: {source}"
    except Exception as e:
        return f"Error playing music: {str(e)}"

def is_process_running(process_name):
    """Check if a process is running."""
    for proc in psutil.process_iter(['name']):
        if process_name.lower() in proc.info['name'].lower():
            return True
    return False

def describe_camera() -> str:
    """
    TODO: Implement camera image description using OpenCV and MobileNet SSD.
    """
    return "TODO: Describe what's in front of the camera."

def get_weather(city: str) -> str:
    """
    TODO: Implement weather fetching using a weather API.
    """
    return f"TODO: Fetch weather for {city}."

def send_email(to: str, subject: str, body: str) -> str:
    """
    TODO: Implement email sending using smtplib.
    """
    return f"TODO: Send email to {to} with subject: {subject}." 