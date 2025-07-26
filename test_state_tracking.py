#!/usr/bin/env python3
"""
Test BAML streaming with proper StreamState tracking
"""

import asyncio
from fast_transition_processor import FastTransitionProcessor
from baml_client.async_client import b

async def main():
    """Run the state tracking demonstration"""
    
    # Example 1: Academic researcher (should be verified)
    print("Example 1: Academic Researcher")
    print("=" * 60)
    
    processor = FastTransitionProcessor()
    
    user_text1 = """
    Dr. Emily Watson is a distinguished professor of Computer Science at Stanford University.
    Contact her at emily.watson@stanford.edu. She's 42 years old and has been teaching 
    for over 15 years. Her research focuses on machine learning and she has published 
    numerous papers in top conferences. As a tenured professor with extensive publications,
    she qualifies for premium access to our research database.
    """
    
    async def process_user_callback(name: str, email: str, is_verified: bool):
        return await b.ProcessUser(name, email, is_verified)
    
    await processor.process_stream(user_text1, process_user_callback)
    
    # Wait a bit between examples
    await asyncio.sleep(2)
    
    # Example 2: Junior developer (not verified, not premium)
    print("\n\nExample 2: Junior Developer")
    print("=" * 60)
    
    processor2 = FastTransitionProcessor()
    
    user_text2 = """
    Alex Johnson is a 24-year-old junior software developer who just started their career.
    You can reach them at alex.j.developer@gmail.com. They recently graduated from a 
    coding bootcamp and are excited to learn more about programming. While enthusiastic,
    they don't have formal academic credentials or extensive experience yet.
    """
    
    await processor2.process_stream(user_text2, process_user_callback)

if __name__ == "__main__":
    asyncio.run(main())