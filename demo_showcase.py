#!/usr/bin/env python3
"""
BAML Streaming Demo Showcase

This demo showcases the key streaming concepts with @stream.with_state:
1. All fields use @stream.with_state for consistent state tracking
2. name + email use @stream.done + @stream.not_null for fast completion
3. bio + age stream incrementally with state information
4. Fast transitions trigger as soon as required fields are complete

To run this demo, you need to set OPENAI_API_KEY environment variable.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def showcase_streaming_concepts():
    """Showcase the key streaming concepts without requiring API calls"""
    
    print("🎯 BAML Streaming Demo: @stream.with_state Usage")
    print("=" * 60)
    
    print("📋 Key Concepts Demonstrated:")
    print("1. ✅ All fields use @stream.with_state for state tracking")
    print("2. ✅ Critical fields (name, email) use @stream.done + @stream.not_null")
    print("3. ✅ Fast transitions trigger when required fields are complete")
    print("4. ✅ useState-like pattern for all field state management")
    print()
    
    # Show BAML configuration
    print("🔧 BAML Configuration:")
    print("""
class UserProfile {
  // Critical fields: complete when ready + track state
  name string @stream.done @stream.not_null @stream.with_state
  email string @stream.done @stream.not_null @stream.with_state
  
  // Optional fields: stream incrementally + track state
  bio string @stream.with_state
  age int @stream.with_state
}""")
    print()
    
    # Show state management
    print("📊 State Management Pattern:")
    from src.streaming_demo import UserProfileState, StreamingProcessor
    from baml_client.baml_client.stream_types import StreamState
    
    state = UserProfileState()
    print(f"Initial state: {state}")
    print()
    
    # Simulate streaming updates
    print("🔄 Simulated Streaming Updates:")
    
    # Name comes in complete (due to @stream.done)
    name_state = StreamState(value="Alice Johnson", state="Complete")
    state.update_field('name', name_state, is_complete=True)
    print(f"✅ Name (Complete): {state.name.value}")
    
    # Email comes in complete (due to @stream.done)
    email_state = StreamState(value="alice.johnson@email.com", state="Complete") 
    state.update_field('email', email_state, is_complete=True)
    print(f"✅ Email (Complete): {state.email.value}")
    print(f"🚀 Required fields ready! Can trigger next job: {state.has_required_fields()}")
    print()
    
    # Bio streams incrementally
    bio_incomplete = StreamState(value="I'm a software engineer...", state="Incomplete")
    state.update_field('bio', bio_incomplete, is_complete=False)
    print(f"🔄 Bio (Incomplete): {state.bio.value}")
    
    bio_complete = StreamState(value="I'm a software engineer with 5 years of experience in Python and AI.", state="Complete")
    state.update_field('bio', bio_complete, is_complete=True)
    print(f"✅ Bio (Complete): {state.bio.value}")
    print()
    
    # Age comes in complete
    age_state = StreamState(value=28, state="Complete")
    state.update_field('age', age_state, is_complete=True)
    print(f"✅ Age (Complete): {state.age.value}")
    print()
    
    print("📈 Final State Summary:")
    print(f"All fields complete: {state.is_complete()}")
    print(f"Required fields ready: {state.has_required_fields()}")
    print()
    
    print("🎉 Demo completed successfully!")
    print("To run with actual LLM calls, set OPENAI_API_KEY and run: python run_demo.py")


if __name__ == "__main__":
    showcase_streaming_concepts()