# -*- coding: utf-8 -*-
"""
Test Voice Timing - Enhanced Zara Voice Interface

This script demonstrates the improved listening durations and timing.
"""

import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_voice_timing():
    """Test the voice timing configuration."""
    print("🎤 Voice Timing Test for Enhanced Zara Interface")
    print("=" * 60)
    
    try:
        from zara.enhanced_voice import EnhancedVoiceInterface
        
        # Create voice interface
        voice = EnhancedVoiceInterface()
        
        print("✅ Enhanced voice interface loaded!")
        print("\n📊 Current Voice Timing Configuration:")
        print("-" * 40)
        print(f"🎤 Wake word detection: {voice.config['wake_word_chunk_duration']} seconds per chunk")
        print(f"💬 Command listening: {voice.config['command_duration']} seconds")
        print(f"⏰ Wake word timeout: {voice.config['wake_word_timeout']} seconds")
        print(f"🕐 Conversation timeout: {voice.config['conversation_timeout']} seconds")
        print(f"🔊 Speech rate: {voice.config['speech_rate']} words per minute")
        print(f"🎛️  Volume: {voice.config['volume']}")
        
        print("\n🎯 What This Means:")
        print("=" * 40)
        print("✨ Wake Word Detection:")
        print(f"   • Listens for 'Zara' in {voice.config['wake_word_chunk_duration']}-second chunks")
        print("   • Continuous listening mode")
        print("   • Natural speech pace supported")
        
        print("\n💬 Command Mode:")
        print(f"   • Full {voice.config['command_duration']} seconds to speak your command")
        print("   • Progress indicator every second")
        print("   • No rush - speak naturally!")
        
        print("\n📧 Email Commands:")
        print("   • 'Zara send email to Amma' (works in 5-second chunks)")
        print("   • 'Zara email Shivani about project saying we should meet tomorrow' (10 seconds)")
        print("   • Plenty of time for complex commands!")
        
        print("\n🚀 Ready to Test?")
        test_choice = input("Would you like to test the voice interface? (yes/no): ").lower().strip()
        
        if test_choice in ['yes', 'y']:
            print("\n🎤 Starting voice test...")
            print("Say 'Zara' to test wake word detection!")
            print("Then try: 'send email to Amma'")
            
            # Run a quick test
            voice.run()
        else:
            print("✅ Configuration looks good! You can start the full interface with:")
            print("   python run_zara_voice.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")

def show_timing_comparison():
    """Show before/after timing comparison."""
    print("\n📈 Timing Improvements:")
    print("=" * 50)
    print("Before (Original):")
    print("  🎤 Wake word: 3 seconds")
    print("  💬 Commands: 5 seconds") 
    print("  ⚡ Felt rushed!")
    
    print("\nAfter (Enhanced):")
    print("  🎤 Wake word: 5 seconds")
    print("  💬 Commands: 10 seconds")
    print("  😌 Natural pace!")
    
    print("\n🎯 Perfect for:")
    print("  • Complex email commands")
    print("  • Natural conversation flow")
    print("  • Users who speak at normal pace")
    print("  • Multi-part instructions")

def main():
    """Main function."""
    show_timing_comparison()
    test_voice_timing()

if __name__ == "__main__":
    main() 