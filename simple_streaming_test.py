#!/usr/bin/env python3
"""
BAML Streaming with Fast Transitions
====================================

Demonstrates real BAML streaming with fast transitions:
- Progressive field streaming with plain field values
- Event-driven processing with `async for partial in stream:`
- Fast transitions when required fields are ready
- Simple state tracking (none → Complete)
- Parallel processing while remaining fields continue streaming
"""

import asyncio
import time
import sys
from dotenv import load_dotenv

# Add baml_client to path
sys.path.insert(0, 'baml_client')
from baml_client import b

# Load environment variables
load_dotenv()

async def demo_baml_streaming_with_fast_transitions():
    """Demonstrate BAML streaming with fast transitions"""
    
    user_text = """
    Dr. Sarah Chen is a distinguished professor of Computer Science at Stanford University.
    Contact her at sarah.chen@stanford.edu. She's 42 years old and has been teaching 
    for over 15 years. Her research focuses on machine learning and she has published 
    numerous papers in top conferences. As a tenured professor with extensive publications,
    she qualifies for premium access to our research database.
    """
    
    print("🚀 BAML Streaming with Fast Transitions")
    print("=" * 60)
    print("Demonstrating progressive field streaming and fast transitions")
    print()
    
    start_time = time.time()
    stream = b.stream.ExtractUserProfile(user_text)
    
    partial_count = 0
    required_fields = ["name", "email", "is_verified"]  # Required fields for fast transition
    fast_transition_triggered = False
    fast_transition_time = None
    
    print("📡 Starting stream processing...")
    
    try:
        # The correct pattern: async for partial in stream
        async for partial_profile in stream:
            partial_count += 1
            elapsed = time.time() - start_time
            
            print(f"\n📊 Partial #{partial_count} at {elapsed:.3f}s:")
            
            # Check field states
            fields = ["name", "email", "is_verified", "bio", "age", "is_premium"]
            field_states = {}
            
            for field_name in fields:
                field_obj = getattr(partial_profile, field_name, None)
                
                # Extract value and state (all fields are now plain values)
                if field_obj is None:
                    value, state = None, "none"
                else:
                    # Plain value - field is complete when it appears
                    value, state = field_obj, "Complete"
                
                field_states[field_name] = (value, state)
                
                # Display field
                marker = "⭐" if field_name in required_fields else "  "
                emoji = "✅" if state == "Complete" else "⏸️"
                
                if value is None:
                    value_str = "[None]"
                elif isinstance(value, str) and len(value) > 30:
                    value_str = f'"{value[:27]}..."'
                else:
                    value_str = str(value)
                
                print(f"{marker} {field_name:6}: {emoji} {state:10} → {value_str}")
            
            # Check for fast transition
            if not fast_transition_triggered:
                required_ready = all(
                    field_states.get(f, (None, "none"))[1] == "Complete" 
                    for f in required_fields
                )
                
                if required_ready:
                    fast_transition_triggered = True
                    fast_transition_time = elapsed
                    print(f"\n🚀 Fast transition at {elapsed:.3f}s!")
                    print(f"   ⏱️ Necessary fields ready after {elapsed:.3f}s")
                    
                    # Extract values for ProcessUser
                    name_val = field_states["name"][0]
                    email_val = field_states["email"][0]
                    
                    print(f"   Calling ProcessUser({name_val}, {email_val})")
                    
                    # Execute ProcessUser asynchronously
                    asyncio.create_task(
                        execute_process_user(name_val, email_val, elapsed)
                    )
        
        if partial_count == 0:
            print("⚠️  No partial updates received - immediate complete response")
    
    except Exception as e:
        print(f"❌ Stream error: {e}")
        print("Error details:", type(e).__name__)
    
    # Get final result
    try:
        final_profile = await stream.get_final_response()
        total_time = time.time() - start_time
        
        print(f"\n" + "=" * 50)
        print(f"✅ Final result after {total_time:.3f}s")
        print(f"📊 Received {partial_count} partial updates")
        
        # Show timing comparison
        if fast_transition_time is not None:
            time_diff = total_time - fast_transition_time
            print(f"⏱️ Time difference: Necessary fields ready at {fast_transition_time:.3f}s")
            print(f"   Final result completed at {total_time:.3f}s")
            print(f"   Additional streaming time: {time_diff:.3f}s ({time_diff/total_time*100:.1f}% of total)")
        
        print(f"\n📋 Final Profile:")
        print(f"   Name: {final_profile.name}")
        print(f"   Email: {final_profile.email}")
        print(f"   Is Verified: {final_profile.is_verified}")
        print(f"   Bio: {final_profile.bio[:50]}..." if final_profile.bio else "   Bio: None")
        print(f"   Age: {final_profile.age}")
        print(f"   Is Premium: {final_profile.is_premium}")
        
    except Exception as e:
        print(f"❌ Final response error: {e}")
    
    # Wait for async tasks
    await asyncio.sleep(1)

async def execute_process_user(name: str, email: str, trigger_time: float):
    """Execute ProcessUser as fast transition"""
    try:
        result = await b.ProcessUser(name, email)
        completion_time = time.time()
        
        print(f"\n   ✅ ProcessUser completed:")
        print(f"      {result}")
        
    except Exception as e:
        print(f"\n   ❌ ProcessUser error: {e}")

if __name__ == "__main__":
    asyncio.run(demo_baml_streaming_with_fast_transitions())