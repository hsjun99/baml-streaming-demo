#!/usr/bin/env python3
"""
BAML Streaming Demo with State Tracking
Handles both StreamState objects and plain values gracefully
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

async def demo_streaming_with_state_tracking():
    """Demonstrate BAML streaming with proper state tracking and fast transitions"""
    
    user_text = """
    Dr. Sarah Chen is a renowned quantum computing researcher at MIT with over 20 years 
    of experience. Contact her at s.chen@mit.edu. At 45 years old, she has published 
    over 100 papers and holds numerous patents. Her groundbreaking work in quantum 
    algorithms has earned her multiple awards. As a senior researcher with extensive 
    credentials, she definitely qualifies for premium membership.
    """
    
    print("🚀 BAML Streaming with Fast Transitions Demo")
    print("=" * 70)
    print("This demo shows how to track field states and trigger fast transitions\n")
    
    start_time = time.time()
    stream = b.stream.ExtractUserProfile(user_text)
    
    required_fields = ["name", "email", "is_verified"]
    has_triggered_fast_transition = False
    update_count = 0
    
    async for partial in stream:
        update_count += 1
        elapsed = time.time() - start_time
        
        print(f"\n📊 Stream Update #{update_count} at {elapsed:.2f}s:")
        print("-" * 50)
        
        # Track field states
        field_info = {}
        for field_name in ["name", "email", "is_verified", "bio", "age", "is_premium"]:
            field_value = getattr(partial, field_name, None)
            
            if field_value is None:
                field_info[field_name] = ("none", None, False)
            elif hasattr(field_value, 'state') and hasattr(field_value, 'value'):
                # It's a StreamState object
                state = field_value.state
                value = field_value.value
                is_complete = (state == "Complete")
                field_info[field_name] = (state, value, is_complete)
            else:
                # Plain value - treat as complete
                field_info[field_name] = ("Complete", field_value, True)
        
        # Display field states
        for field_name, (state, value, is_complete) in field_info.items():
            if state == "none":
                continue
                
            marker = "⭐" if field_name in required_fields else "  "
            
            # State emoji
            if state == "Complete":
                emoji = "✅"
            elif state == "Incomplete":
                emoji = "⏳"
            elif state == "Pending":
                emoji = "⏸️"
            else:
                emoji = "✓"  # For plain values
            
            # Format value
            if value is None:
                value_str = "[None]"
            elif isinstance(value, str) and len(value) > 40:
                value_str = f'"{value[:37]}..."'
            else:
                value_str = f'"{value}"' if isinstance(value, str) else str(value)
            
            print(f"{marker} {field_name:12} : {emoji} {value_str}")
        
        # Check if required fields are complete
        required_complete = all(
            field_info.get(f, ("none", None, False))[2] 
            for f in required_fields
        )
        
        if required_complete and not has_triggered_fast_transition:
            has_triggered_fast_transition = True
            
            print(f"\n🎯 FAST TRANSITION TRIGGERED at {elapsed:.2f}s!")
            print("   All required fields (⭐) are ready!\n")
            
            # Extract values (handle both StreamState and plain values)
            name = field_info["name"][1]
            email = field_info["email"][1]
            is_verified = field_info["is_verified"][1]
            
            print(f"   Executing ProcessUser with:")
            print(f"   - Name: {name}")
            print(f"   - Email: {email}")
            print(f"   - Verified: {is_verified}")
            
            # Execute next job asynchronously
            async def process_next_job():
                job_start = time.time() - start_time
                result = await b.ProcessUser(name, email, is_verified)
                job_end = time.time() - start_time
                print(f"\n   💬 ProcessUser completed at {job_end:.2f}s (took {job_end - job_start:.2f}s):")
                print(f"      {result}")
            
            asyncio.create_task(process_next_job())
    
    # Get final response
    final = await stream.get_final_response()
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print("✅ Streaming Complete - Final Profile:")
    print(f"   Name: {final.name}")
    print(f"   Email: {final.email}")
    print(f"   Verified: {final.is_verified}")
    print(f"   Premium: {final.is_premium}")
    print(f"\n⏱️  Total streaming time: {total_time:.2f}s")
    
    # Demonstrate timing advantage
    print("\n🎯 Fast Transition Benefits:")
    print("   - Started next job as soon as required fields were ready")
    print("   - Continued streaming optional fields in parallel")
    print("   - Reduced overall latency for user-facing operations")
    
    # Wait for async tasks
    await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(demo_streaming_with_state_tracking())