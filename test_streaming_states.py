#!/usr/bin/env python3
"""
Test BAML streaming with StreamState tracking
Shows how field states transition from Pending -> Incomplete -> Complete
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

async def track_streaming_states():
    """Track how StreamState objects change during streaming"""
    
    user_text = """
    Dr. Emily Watson is a distinguished professor of Computer Science at Stanford University.
    Contact her at emily.watson@stanford.edu. She's 42 years old and has been teaching 
    for over 15 years. Her research focuses on machine learning and she has published 
    numerous papers in top conferences. As a tenured professor with extensive publications,
    she qualifies for premium access to our research database.
    """
    
    print("🔬 BAML StreamState Tracking Demo")
    print("=" * 70)
    print("This demo shows how field states transition during streaming:\n")
    print("States: Pending → Incomplete → Complete\n")
    
    start_time = time.time()
    stream = b.stream.ExtractUserProfile(user_text)
    
    update_count = 0
    required_complete_time = None
    has_triggered_fast_transition = False
    
    async for partial in stream:
        update_count += 1
        elapsed = time.time() - start_time
        
        print(f"\n📊 Update #{update_count} at {elapsed:.2f}s:")
        print("-" * 50)
        
        # Track each field's state
        fields = {
            "name": ("⭐", partial.name),
            "email": ("⭐", partial.email), 
            "is_verified": ("⭐", partial.is_verified),
            "bio": ("  ", partial.bio),
            "age": ("  ", partial.age),
            "is_premium": ("  ", partial.is_premium)
        }
        
        required_complete = True
        
        for field_name, (marker, field_value) in fields.items():
            if field_value is None:
                print(f"{marker} {field_name:12} : [None]")
                if marker == "⭐":
                    required_complete = False
            else:
                # All fields should have StreamState with @stream.with_state
                state = field_value.state
                value = field_value.value
                
                # State emoji
                if state == "Complete":
                    state_emoji = "✅"
                elif state == "Incomplete":
                    state_emoji = "⏳"
                else:  # Pending
                    state_emoji = "⏸️"
                
                # Format value
                if value is None:
                    value_display = "[None]"
                elif isinstance(value, str) and len(value) > 40:
                    value_display = f'"{value[:37]}..."'
                else:
                    value_display = f'"{value}"' if isinstance(value, str) else str(value)
                
                print(f"{marker} {field_name:12} : {state_emoji} {state:10} → {value_display}")
                
                # Check if required field is complete
                if marker == "⭐" and state != "Complete":
                    required_complete = False
        
        # Trigger fast transition when required fields are complete
        if required_complete and not has_triggered_fast_transition:
            has_triggered_fast_transition = True
            required_complete_time = elapsed
            
            print(f"\n🚀 FAST TRANSITION TRIGGERED at {elapsed:.2f}s!")
            print("   All required fields (⭐) are Complete!")
            
            # Extract values for ProcessUser
            name = partial.name.value
            email = partial.email.value
            is_verified = partial.is_verified.value
            
            print(f"\n   Calling ProcessUser with:")
            print(f"   - Name: {name}")
            print(f"   - Email: {email}")
            print(f"   - Verified: {is_verified}")
            
            # Execute ProcessUser asynchronously
            async def run_next_job():
                job_start = time.time()
                result = await b.ProcessUser(name, email, is_verified)
                job_elapsed = time.time() - job_start
                total_elapsed = time.time() - start_time
                print(f"\n   💬 ProcessUser completed in {job_elapsed:.2f}s (total: {total_elapsed:.2f}s):")
                print(f"      {result}")
            
            asyncio.create_task(run_next_job())
    
    # Get final response
    final = await stream.get_final_response()
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("✅ Stream Complete - Final Profile:")
    print(f"   Name: {final.name}")
    print(f"   Email: {final.email}")
    print(f"   Verified: {final.is_verified}")
    print(f"   Premium: {final.is_premium}")
    print(f"   Total streaming time: {total_time:.2f}s")
    
    if required_complete_time:
        print(f"\n🎯 Fast Transition Benefit:")
        print(f"   Required fields ready at: {required_complete_time:.2f}s")
        print(f"   Full stream completed at: {total_time:.2f}s")
        print(f"   Time saved: {total_time - required_complete_time:.2f}s")
    
    # Wait for async tasks
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(track_streaming_states())