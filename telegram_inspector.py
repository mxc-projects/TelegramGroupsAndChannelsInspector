#!/usr/bin/env python3
"""
Telegram Groups Inspector - Quick Launch Script
Main entry point for the application
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

if __name__ == "__main__":
    try:
        from src.main import main

        main()
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print(
            "💡 Make sure all dependencies are installed: pip install -r requirements.txt"
        )
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        sys.exit(1)
