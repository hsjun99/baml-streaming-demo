#!/usr/bin/env python3
"""Test script to verify all imports work correctly"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_imports():
    """Test all imports"""
    try:
        print("Testing imports...")
        
        from src.streaming_demo import UserProfileState, StreamingProcessor
        from baml_client.baml_client.stream_types import StreamState
        print("✅ streaming_demo imports successful")
        
        # Test the state class
        state = UserProfileState()
        print(f"✅ UserProfileState created: {state}")
        
        # Test field update with StreamState objects
        name_stream_state = StreamState(value='Alice', state="Complete")
        state.update_field('name', name_stream_state, is_complete=True)
        print(f"✅ Field update works: name = {state.name.value if state.name else None}, complete = {state.name_complete}")
        
        # Test required fields check
        email_stream_state = StreamState(value='alice@example.com', state="Complete")
        state.update_field('email', email_stream_state, is_complete=True)
        has_required = state.has_required_fields()
        print(f"✅ Required fields check: {has_required}")
        
        # Test processor creation
        processor = StreamingProcessor()
        print(f"✅ StreamingProcessor created: {processor}")
        
        print("\n🎉 All tests passed! Ready to run the demo.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)