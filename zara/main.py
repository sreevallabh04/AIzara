from zara.agent import generate_response
from zara.voice import take_command, talk
import threading
import time
import sys

class ZaraAssistant:
    def __init__(self):
        self.is_active = False
        self.continuous_mode = False
        self.conversation_history = []
    
    def start(self):
        """Start the Zara assistant."""
        talk("Hello! I'm Zara, your personal assistant. How can I help you today?")
        self.is_active = True
        
        while self.is_active:
            try:
                # Listen for command
                command = take_command()
                
                if not command:
                    continue
                
                # Check for special commands
                if "activate assistant mode" in command.lower():
                    self.continuous_mode = True
                    talk("Assistant mode activated. I'll keep listening for your commands.")
                    continue
                
                if "deactivate assistant mode" in command.lower():
                    self.continuous_mode = False
                    talk("Assistant mode deactivated. I'll only respond when you call me.")
                    continue
                
                if "goodbye" in command.lower() or "exit" in command.lower():
                    talk("Goodbye! Have a great day!")
                    self.is_active = False
                    break
                
                # Generate and speak response
                print(f"Processing command: {command}")
                response = generate_response(command, self.conversation_history)
                print(f"Response: {response}")
                talk(response)
                
                # Update conversation history
                self.conversation_history.append((command, response))
                if len(self.conversation_history) > 10:  # Keep last 10 exchanges
                    self.conversation_history.pop(0)
                
                # If in continuous mode, wait a bit before listening again
                if self.continuous_mode:
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\nShutting down Zara...")
                self.is_active = False
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                talk("I encountered an error. Please try again.")
    
    def stop(self):
        """Stop the Zara assistant."""
        self.is_active = False
        talk("Shutting down. Goodbye!")

def run_zara():
    """Main entry point for the Zara assistant."""
    try:
        assistant = ZaraAssistant()
        assistant.start()
    except KeyboardInterrupt:
        print("\nShutting down Zara...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        sys.exit(0)

if __name__ == "__main__":
    run_zara() 