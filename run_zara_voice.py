# -*- coding: utf-8 -*-
"""
Zara Assistant - Enhanced Voice Interface Launcher

This script starts Zara with the new conversational voice interface that includes:
- Wake word detection ("Zara")
- Natural conversation flow
- Contact-based email automation
- Better error handling
"""

import sys
import os

# Add the project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Launch the enhanced Zara voice interface."""
    print("🚀 Starting Zara Assistant with Enhanced Voice Interface")
    print("=" * 60)
    
    try:
        from zara.enhanced_voice import run_enhanced_voice
        
        print("✅ Enhanced voice interface loaded successfully!")
        print("🎤 Features available:")
        print("   • Wake word detection ('Zara')")
        print("   • Natural conversation flow")
        print("   • Contact-based email automation")
        print("   • Voice command: 'Zara send email to Amma'")
        print("   • Voice command: 'Zara email Shivani about project'")
        print("   • And much more!")
        print()
        
        # Start the enhanced voice interface
        run_enhanced_voice()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error starting enhanced voice interface: {e}")
        
        # Fallback to basic voice interface
        print("\n🔄 Falling back to basic voice interface...")
        try:
            from zara.main import run_zara
            run_zara()
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            print("Please check your configuration and try again.")

if __name__ == "__main__":
    main() 