"""
Zara Assistant - An offline-first voice assistant powered by local LLMs.
Entry point for running the Zara assistant with all modules integrated.
"""

import asyncio
import os
import sys
import time
import signal
import webbrowser
import platform
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Import Zara components
from zara.logger import get_logger
from zara.memory import get_memory_manager
from zara.vision import get_vision_system

# Load environment variables
load_dotenv()

# Setup logger
logger = get_logger()

# Initialize components
memory = None
agent = None
voice = None
vision = None

# Feature flags based on available dependencies
FEATURES = {
    "voice": False,
    "agent": False,
    "vision": False,
    "memory": False
}

class Colors:
    """Terminal colors for better user experience."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color=Colors.BLUE, bold=False):
    """Print colored text to the terminal."""
    prefix = ""
    if bold:
        prefix += Colors.BOLD
    print(f"{prefix}{color}{text}{Colors.ENDC}")

def initialize_components(skip_checks=False):
    """Initialize all Zara components with error handling."""
    global memory, agent, voice, vision, FEATURES
    
    try:
        # Create necessary directories
        Path("data").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        Path("models").mkdir(exist_ok=True)
        Path("config").mkdir(exist_ok=True)
        
        # Initialize memory system
        logger.info("Initializing memory system...")
        memory = get_memory_manager()
        FEATURES["memory"] = True
        
        # Initialize vision system
        logger.info("Initializing vision system...")
        try:
            vision = get_vision_system()
            FEATURES["vision"] = True
        except Exception as e:
            logger.warning(f"Vision system initialization failed: {str(e)}")
            print_colored("Vision features will not be available.", Colors.YELLOW)
        
        # Initialize voice interface if possible
        logger.info("Initializing voice interface...")
        try:
            from zara.voice import get_voice_interface
            voice = get_voice_interface()
            FEATURES["voice"] = True
        except Exception as e:
            logger.warning(f"Voice interface initialization failed: {str(e)}")
            print_colored("Voice features will not be available. Using text mode instead.", Colors.YELLOW)
        
        # Initialize agent with Ollama if available and not skipped
        if not skip_checks and check_ollama_running() and check_llama_model():
            logger.info("Initializing agent with Ollama LLM...")
            try:
                from zara.agent import get_agent
                agent = get_agent()
                FEATURES["agent"] = True
            except Exception as e:
                logger.warning(f"Agent initialization failed: {str(e)}")
                print_colored("AI agent features will not be available.", Colors.YELLOW)
        elif not skip_checks:
            logger.warning("Ollama or LLaMA model not available. Agent functionality disabled.")
            print_colored("AI agent features will not be available. Use --setup to configure Ollama.", Colors.YELLOW)
        
        available_features = [k for k, v in FEATURES.items() if v]
        logger.info(f"Components initialized with features: {', '.join(available_features)}")
        
        if all(FEATURES.values()):
            print_colored("All systems initialized successfully!", Colors.GREEN, bold=True)
        else:
            print_colored("Zara initialized with limited functionality.", Colors.YELLOW, bold=True)
            print_colored("Run with --setup to configure missing components.", Colors.YELLOW)
        
        return True
    
    except Exception as e:
        logger.critical(f"Failed to initialize components: {str(e)}")
        print_colored(f"Initialization error: {str(e)}", Colors.RED, bold=True)
        return False

def check_ollama_running():
    """Check if Ollama service is running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except Exception:
        return False

def check_llama_model():
    """Check if LLaMA model is pulled."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        data = response.json()
        # Accept both 'llama3.2' and 'llama3.2:latest'
        return any(
            model.get('name', '').startswith('llama3.2')
            for model in data.get('models', [])
        )
    except Exception:
        return False

def install_ollama():
    """Provide instructions and assistance for installing Ollama."""
    system = platform.system()
    
    print_colored("\n=== OLLAMA INSTALLATION GUIDE ===", Colors.HEADER, bold=True)
    print_colored("Ollama is required for Zara's AI capabilities.\n", Colors.BLUE)
    
    if system == "Windows":
        print_colored("1. Download Ollama for Windows:", Colors.GREEN)
        print("   https://ollama.ai/download/windows")
        
        open_browser = input("Would you like to open the download page now? (y/n): ").lower() == 'y'
        if open_browser:
            webbrowser.open("https://ollama.ai/download/windows")
        
        print_colored("\n2. Install Ollama following the on-screen instructions", Colors.GREEN)
        print_colored("\n3. Once installed, run Ollama from the Start menu", Colors.GREEN)
        
    elif system == "Darwin":  # macOS
        print_colored("1. Install Ollama using the following command:", Colors.GREEN)
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        
        execute_cmd = input("Would you like to run this command now? (y/n): ").lower() == 'y'
        if execute_cmd:
            subprocess.run("curl -fsSL https://ollama.ai/install.sh | sh", shell=True)
        
        print_colored("\n2. Start Ollama by running:", Colors.GREEN)
        print("   ollama serve")
        
    elif system == "Linux":
        print_colored("1. Install Ollama using the following command:", Colors.GREEN)
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        
        execute_cmd = input("Would you like to run this command now? (y/n): ").lower() == 'y'
        if execute_cmd:
            subprocess.run("curl -fsSL https://ollama.ai/install.sh | sh", shell=True)
        
        print_colored("\n2. Start Ollama by running:", Colors.GREEN)
        print("   ollama serve")
    
    print_colored("\nAfter installing Ollama, restart Zara Assistant.", Colors.BLUE, bold=True)
    return True

def download_llama_model():
    """Download the LLaMA model using Ollama."""
    print_colored("\n=== DOWNLOADING LLAMA MODEL ===", Colors.HEADER, bold=True)
    print_colored("This may take a while depending on your internet connection.", Colors.YELLOW)
    
    try:
        if not check_ollama_running():
            print_colored("Ollama is not running. Please start Ollama first.", Colors.RED)
            return False
        
        print("Running: ollama pull llama3")
        subprocess.run(["ollama", "pull", "llama3"], check=True)
        
        print_colored("\nLLaMA model downloaded successfully!", Colors.GREEN, bold=True)
        return True
    except subprocess.SubprocessError as e:
        print_colored(f"Error downloading LLaMA model: {str(e)}", Colors.RED)
        return False
    except FileNotFoundError:
        print_colored("Ollama command not found. Please make sure Ollama is installed correctly.", Colors.RED)
        return False

def system_checks():
    """Perform system checks and setup."""
    # Check for Ollama
    ollama_running = check_ollama_running()
    if not ollama_running:
        print_colored("❌ Ollama service not detected.", Colors.RED)
        print_colored("   Please install Ollama from https://ollama.ai/download", Colors.YELLOW)
        print_colored("   and start it with 'ollama serve'", Colors.YELLOW)
        print_colored("   Use --setup for guided installation", Colors.YELLOW)
    else:
        print_colored("✓ Ollama service is running", Colors.GREEN)
    
    # Check for LLaMA model
    llama_available = check_llama_model()
    if not llama_available:
        print_colored("❌ LLaMA model not found.", Colors.RED)
        print_colored("   Please pull it with 'ollama pull llama3'", Colors.YELLOW)
        print_colored("   Use --setup for guided installation", Colors.YELLOW)
    else:
        print_colored("✓ LLaMA model is available", Colors.GREEN)
    
    return ollama_running and llama_available

def setup_wizard():
    """Interactive setup wizard for Zara Assistant."""
    print_colored("\n=== ZARA ASSISTANT SETUP WIZARD ===", Colors.HEADER, bold=True)
    print_colored("This wizard will help you set up all required components for Zara.", Colors.BLUE)
    
    # Check Ollama
    print_colored("\nChecking for Ollama...", Colors.BLUE)
    if not check_ollama_running():
        print_colored("Ollama not detected or not running.", Colors.YELLOW)
        install_ollama()
        print_colored("\nAfter installing and starting Ollama, press Enter to continue...", Colors.BLUE)
        input()
    else:
        print_colored("✓ Ollama is running", Colors.GREEN)
    
    # Check LLaMA model
    print_colored("\nChecking for LLaMA model...", Colors.BLUE)
    if not check_llama_model():
        print_colored("LLaMA model not found.", Colors.YELLOW)
        download = input("Would you like to download the LLaMA model now? (y/n): ").lower() == 'y'
        if download:
            download_llama_model()
    else:
        print_colored("✓ LLaMA model is available", Colors.GREEN)
    
    print_colored("\nSetup complete! You can now start Zara Assistant.", Colors.GREEN, bold=True)
    
    start_now = input("Would you like to start Zara Assistant now? (y/n): ").lower() == 'y'
    return start_now

def signal_handler(sig, frame):
    """Handle interrupt signals gracefully."""
    print_colored("\nShutting down Zara Assistant...", Colors.YELLOW)
    
    # Clean up resources
    if voice and FEATURES["voice"]:
        logger.info("Shutting down voice interface...")
    
    logger.info("Shutdown complete")
    sys.exit(0)

async def handle_user_interaction():
    """Main interaction loop with error handling."""
    logger.info("Entered handle_user_interaction() main loop")
    if not FEATURES["voice"]:
        print_colored("Voice features are not available.", Colors.RED)
        print_colored("Falling back to text mode.", Colors.YELLOW)
        text_mode_interaction()
        return
        
    if not FEATURES["agent"]:
        print_colored("Agent features are not available.", Colors.RED)
        print_colored("Voice commands will be processed with limited capabilities.", Colors.YELLOW)
        
        # Welcome message with limited functionality warning
        voice.speak("Hello! I am Zara. I'm running with limited capabilities because the LLaMA model is not available. I can respond to basic commands only.")
        
        # Basic voice command set
        async def simple_voice_process(cmd):
            cmd = cmd.lower().strip()
            if "time" in cmd:
                import datetime
                return f"Current time is {datetime.datetime.now().strftime('%I:%M %p')}"
            elif "date" in cmd:
                import datetime
                return f"Today's date is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"
            elif "hello" in cmd or "hi" in cmd:
                return "Hello! I'm running with limited capabilities without the LLaMA model."
            elif "help" in cmd:
                return ("I can tell you the time, date, or respond to greetings. "
                        "For full functionality, please set up the LLaMA model.")
            else:
                return ("I'm running in basic mode without the LLaMA model. "
                        "My capabilities are limited. Ask for help to learn what I can do.")
        
        # Limited voice interaction loop
        while True:
            try:
                # Listen for user input
                logger.info("About to call voice.listen()")
                user_input = await voice.listen()
                logger.info(f"voice.listen() returned: {user_input}")
                
                if not user_input:
                    logger.info("No input detected")
                    continue
                
                # Simple processing
                logger.info(f"Processing (basic mode): {user_input}")
                response = await simple_voice_process(user_input)
                
                # Speak response
                logger.info(f"Responding: {response}")
                voice.speak(response)
                
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                error_msg = f"Error during interaction: {str(e)}"
                logger.error(error_msg)
                voice.speak("I'm sorry, I encountered an error. Let me try again.")
        
        return
    
    # Full functionality with voice and agent
    # Welcome message
    voice.speak("Hello! I am Zara, your voice assistant. How can I help you today?")
    
    while True:
        try:
            # Listen for user input
            logger.info("About to call voice.listen()")
            user_input = await voice.listen()
            logger.info(f"voice.listen() returned: {user_input}")
            
            if not user_input:
                logger.info("No input detected")
                continue
            
            # Process with agent
            logger.info(f"Processing: {user_input}")
            response = await agent.process_message(user_input)
            
            # Speak response
            logger.info(f"Responding: {response}")
            voice.speak(response)
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            break
        except Exception as e:
            error_msg = f"Error during interaction: {str(e)}"
            logger.error(error_msg)
            voice.speak("I'm sorry, I encountered an error. Let me try again.")

def text_mode_interaction():
    """Fallback text-based interaction when voice is not available."""
    print_colored("\n=== ZARA TEXT MODE ===", Colors.HEADER, bold=True)
    
    if not FEATURES["agent"]:
        print_colored("AI agent features are not available - Running in basic mode.", Colors.YELLOW)
        print_colored("Commands will be processed locally with limited capabilities.", Colors.YELLOW)
        print_colored("Type 'exit' or 'quit' to end the session.", Colors.BLUE)
        
        # Basic command set when agent is unavailable
        def simple_process(cmd):
            cmd = cmd.lower().strip()
            if "time" in cmd:
                import datetime
                return f"Current time is {datetime.datetime.now().strftime('%I:%M %p')}"
            elif "date" in cmd:
                import datetime
                return f"Today's date is {datetime.datetime.now().strftime('%A, %B %d, %Y')}"
            elif "hello" in cmd or "hi" in cmd:
                return "Hello! I'm running with limited capabilities without the LLaMA model."
            elif "help" in cmd:
                return ("Available commands: time, date, hello, help, exit\n"
                        "For full functionality, run with --setup to configure the LLaMA model.")
            else:
                return ("I'm running in basic mode without the LLaMA model. "
                        "My capabilities are limited. Type 'help' for available commands.")
        
        # Basic interaction loop
        while True:
            try:
                # Get text input
                user_input = input("\nYou: ")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print_colored("Goodbye!", Colors.GREEN)
                    break
                
                # Simple local processing
                logger.info(f"Processing (basic mode): {user_input}")
                response = simple_process(user_input)
                
                # Display response
                print_colored(f"Zara: {response}", Colors.GREEN)
                
            except KeyboardInterrupt:
                print_colored("\nGoodbye!", Colors.GREEN)
                break
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(error_msg)
                print_colored(f"Error: {error_msg}", Colors.RED)
    else:
        # Full text mode with agent
        print_colored("Using text mode with full AI capabilities.", Colors.GREEN)
        print_colored("Type 'exit' or 'quit' to end the session.", Colors.BLUE)
        
        while True:
            try:
                # Get text input
                user_input = input("\nYou: ")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print_colored("Goodbye!", Colors.GREEN)
                    break
                
                # Process with agent
                logger.info(f"Processing: {user_input}")
                response = agent.process_message(user_input)
                
                # Display response
                print_colored(f"Zara: {response}", Colors.GREEN)
                
            except KeyboardInterrupt:
                print_colored("\nGoodbye!", Colors.GREEN)
                break
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(error_msg)
                print_colored(f"Error: {error_msg}", Colors.RED)

def create_first_run_preference():
    """Create a record of first run in preferences."""
    try:
        if FEATURES["memory"]:
            # Set preference to indicate first run is complete
            memory.set_preference("first_run_complete", True)
            memory.set_preference("first_run_date", time.strftime("%Y-%m-%d %H:%M:%S"))
            logger.info("First run preferences stored")
    except Exception as e:
        logger.error(f"Failed to store first run preference: {str(e)}")

def check_first_run():
    """Check if this is the first run and handle onboarding."""
    try:
        if not FEATURES["memory"]:
            return False
            
        first_run_complete = memory.get_preference("first_run_complete", False)
        if not first_run_complete:
            logger.info("First run detected - performing onboarding")
            
            if FEATURES["voice"]:
                voice.speak(
                    "Welcome to Zara Assistant! This appears to be your first time running me. "
                    "I'm an offline-first voice assistant powered by local language models. "
                    "You can ask me questions, give me tasks, or just chat. "
                    "I'm now set up and ready to help you!"
                )
            else:
                print_colored(
                    "Welcome to Zara Assistant! This appears to be your first time running me.\n"
                    "I'm an offline-first assistant powered by local language models.\n"
                    "You can ask me questions, give me tasks, or just chat.\n"
                    "I'm now set up and ready to help you!",
                    Colors.GREEN, bold=True
                )
                
            create_first_run_preference()
        return not first_run_complete
    except Exception as e:
        logger.error(f"Failed to check first run status: {str(e)}")
        return False

def print_usage():
    """Print usage information."""
    print_colored("\n=== ZARA ASSISTANT USAGE ===", Colors.HEADER, bold=True)
    print_colored("Zara is an offline-first voice assistant powered by local LLMs.\n", Colors.BLUE)
    
    print_colored("Command line options:", Colors.GREEN)
    print("  --help      Show this help message")
    print("  --setup     Run the interactive setup wizard")
    print("  --check     Run system checks without starting the assistant")
    print("  --force     Start with available features, skipping dependency checks")
    print("  --text      Force text mode interaction (no voice)")
    
    print_colored("\nExamples:", Colors.GREEN)
    print("  python main.py             # Start Zara normally")
    print("  python main.py --setup     # Run setup wizard")
    print("  python main.py --force     # Start with available features")

def main():
    """Main entry point for Zara Assistant."""
    args = sys.argv[1:]
    
    # Show usage
    if "--help" in args or "-h" in args:
        print_usage()
        return 0
    
    print_colored("\n=== ZARA ASSISTANT ===", Colors.HEADER, bold=True)
    logger.info("Starting Zara Assistant")
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize components (do not skip checks)
    if not initialize_components(skip_checks=False):
        logger.error("Failed to initialize components. Exiting.")
        return 1
    
    # Check that all features are available
    missing = [k for k, v in FEATURES.items() if not v]
    if missing:
        logger.critical(f"Missing required features: {', '.join(missing)}. Exiting.")
        print_colored(f"Error: Missing required features: {', '.join(missing)}. Please ensure all dependencies are installed and configured.", Colors.RED, bold=True)
        return 1
    logger.info(f"All required features initialized: {', '.join([k for k, v in FEATURES.items() if v])}")
    
    try:
        if "--text" in args or not FEATURES["voice"]:
            text_mode_interaction()
        else:
            asyncio.run(handle_user_interaction())
    except Exception as e:
        logger.critical(f"Fatal error in main loop: {str(e)}")
        if FEATURES["voice"]:
            voice.speak("I'm sorry, I've encountered a critical error and need to shut down.")
        print_colored(f"Fatal error: {str(e)}", Colors.RED, bold=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())