#!/usr/bin/env python3
"""
BAML Streaming Demo Runner

This script demonstrates fast transitions in BAML streaming:
1. Extracts a user profile with 4 fields (name, email, bio, age)
2. Uses @stream.done for critical fields (name, email)
3. Triggers the next job as soon as name + email are available
4. Shows state management with useState-like pattern

Requirements:
- Set OPENAI_API_KEY environment variable
- Install dependencies with: poetry install
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Check for environment variable
if not os.getenv("OPENAI_API_KEY"):
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    print("Please set it with: export OPENAI_API_KEY=your_api_key")
    print("Or create a .env file based on .env.example")
    sys.exit(1)

# Import and run the demo
try:
    from streaming_demo import demo
    import asyncio
    
    if __name__ == "__main__":
        asyncio.run(demo())
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to run: poetry install")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running demo: {e}")
    sys.exit(1)