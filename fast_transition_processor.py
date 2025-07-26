#!/usr/bin/env python3
"""
Fast Transition Processor with Proper State Tracking
====================================================

This module implements real BAML streaming state tracking using StreamState objects.
It monitors field completion states and triggers fast transitions when required fields
are marked as "complete" in their StreamState metadata.
"""

import asyncio
import time
from typing import Optional, Callable
from dataclasses import dataclass
from dotenv import load_dotenv

from baml_client.async_client import b
from baml_client.stream_types import UserProfile

# Load environment variables
load_dotenv()

@dataclass
class TransitionMetrics:
    """Tracks timing metrics for fast transitions"""
    stream_start_time: float
    required_fields_ready_time: Optional[float] = None
    all_fields_ready_time: Optional[float] = None
    next_job_start_time: Optional[float] = None
    next_job_complete_time: Optional[float] = None

class FastTransitionProcessor:
    """
    Processes BAML streaming with fast transitions based on StreamState completion.
    
    This processor monitors the actual StreamState objects returned by BAML to detect
    when required fields transition from "incomplete" to "complete" state.
    """
    
    def __init__(self):
        self.metrics = None
        self.has_triggered_fast_transition = False
        self.required_fields = ["name", "email", "is_verified"]
        
    def _check_required_fields_complete(self, profile: UserProfile) -> bool:
        """
        Check if all required fields have reached 'complete' state.
        
        For fields with @stream.with_state, we check the StreamState.state property.
        """
        # Check each required field's StreamState
        for field_name in self.required_fields:
            field_value = getattr(profile, field_name, None)
            
            if field_value is None:
                return False
                
            # Check if it's a StreamState object
            if hasattr(field_value, 'state'):
                # It's a StreamState object - check completion state
                if field_value.state != "Complete":
                    return False
            else:
                # For @stream.done fields without state, presence means complete
                # But since we're using @stream.with_state, this shouldn't happen
                pass
                
        return True
    
    def _check_all_fields_complete(self, profile: UserProfile) -> bool:
        """Check if all fields (required + optional) are complete"""
        all_fields = ["name", "email", "is_verified", "bio", "age", "is_premium"]
        
        for field_name in all_fields:
            field_value = getattr(profile, field_name, None)
            
            if field_value is None:
                return False
                
            # Check StreamState completion
            if hasattr(field_value, 'state'):
                if field_value.state != "Complete":
                    return False
                    
        return True
    
    async def process_stream(self, user_text: str, on_fast_transition: Optional[Callable] = None):
        """
        Process a BAML stream with proper state tracking.
        
        Args:
            user_text: Input text to extract user profile from
            on_fast_transition: Callback when required fields are ready
        """
        self.metrics = TransitionMetrics(stream_start_time=time.time())
        self.has_triggered_fast_transition = False
        
        print("\n🔄 Starting BAML stream with state tracking...")
        print("=" * 60)
        
        # Start the BAML stream
        stream = b.stream.ExtractUserProfile(user_text)
        
        # Track partial updates
        update_count = 0
        
        async for partial_profile in stream:
            update_count += 1
            current_time = time.time() - self.metrics.stream_start_time
            
            # Log field states
            print(f"\n📊 Update #{update_count} at {current_time:.2f}s:")
            self._log_field_states(partial_profile)
            
            # Check for fast transition trigger
            if not self.has_triggered_fast_transition:
                if self._check_required_fields_complete(partial_profile):
                    self.has_triggered_fast_transition = True
                    self.metrics.required_fields_ready_time = time.time()
                    
                    print(f"\n🚀 FAST TRANSITION TRIGGERED at {current_time:.2f}s!")
                    print("   Required fields are complete. Starting next job...")
                    
                    # Extract clean values from StreamState objects
                    name_value = partial_profile.name.value if hasattr(partial_profile.name, 'value') else partial_profile.name
                    email_value = partial_profile.email.value if hasattr(partial_profile.email, 'value') else partial_profile.email
                    is_verified_value = partial_profile.is_verified.value if hasattr(partial_profile.is_verified, 'value') else partial_profile.is_verified
                    
                    if on_fast_transition:
                        asyncio.create_task(
                            self._execute_next_job(
                                name_value, 
                                email_value, 
                                is_verified_value,
                                on_fast_transition
                            )
                        )
            
            # Check if all fields are complete
            if self._check_all_fields_complete(partial_profile):
                if not self.metrics.all_fields_ready_time:
                    self.metrics.all_fields_ready_time = time.time()
                    print(f"\n✅ All fields complete at {current_time:.2f}s")
        
        # Get final response
        final_profile = await stream.get_final_response()
        print("\n📋 Stream completed. Final profile received.")
        
        # Display timing analysis
        self._display_timing_analysis()
        
        return final_profile
    
    def _log_field_states(self, profile: UserProfile):
        """Log the state of each field with StreamState information"""
        fields = ["name", "email", "is_verified", "bio", "age", "is_premium"]
        
        for field_name in fields:
            field_value = getattr(profile, field_name, None)
            
            if field_value is None:
                print(f"   {field_name}: None")
            elif hasattr(field_value, 'state') and hasattr(field_value, 'value'):
                # It's a StreamState object
                state = field_value.state
                value = field_value.value
                
                # Format value display
                if isinstance(value, str) and len(value) > 50:
                    value_display = f"{value[:47]}..."
                else:
                    value_display = str(value)
                
                # Use emojis to indicate state
                state_emoji = "✅" if state == "Complete" else "⏳" if state == "Incomplete" else "⏸️"
                required_marker = "⭐" if field_name in self.required_fields else "  "
                
                print(f"   {required_marker} {field_name}: {state_emoji} {state} - {value_display}")
            else:
                # Direct value (shouldn't happen with @stream.with_state)
                print(f"   {field_name}: {field_value}")
    
    async def _execute_next_job(self, name: str, email: str, is_verified: bool, callback: Callable):
        """Execute the next job asynchronously"""
        self.metrics.next_job_start_time = time.time()
        
        # Call the ProcessUser function
        result = await callback(name, email, is_verified)
        
        self.metrics.next_job_complete_time = time.time()
        elapsed = self.metrics.next_job_complete_time - self.metrics.stream_start_time
        
        print(f"\n💬 Next job completed at {elapsed:.2f}s:")
        print(f"   {result}")
    
    def _display_timing_analysis(self):
        """Display comprehensive timing analysis"""
        if not self.metrics:
            return
            
        print("\n" + "=" * 60)
        print("⏱️  TIMING ANALYSIS")
        print("=" * 60)
        
        if self.metrics.required_fields_ready_time:
            req_time = self.metrics.required_fields_ready_time - self.metrics.stream_start_time
            print(f"Required fields ready: {req_time:.2f}s")
        
        if self.metrics.all_fields_ready_time:
            all_time = self.metrics.all_fields_ready_time - self.metrics.stream_start_time
            print(f"All fields ready: {all_time:.2f}s")
        
        if self.metrics.next_job_complete_time:
            job_time = self.metrics.next_job_complete_time - self.metrics.stream_start_time
            print(f"Next job completed: {job_time:.2f}s")
            
            # Calculate improvement
            if self.metrics.all_fields_ready_time:
                improvement = all_time - job_time
                percentage = (improvement / all_time) * 100
                print(f"\n🚀 Fast transition saved: {improvement:.2f}s ({percentage:.1f}% faster)")

async def main():
    """Demonstrate fast transitions with real BAML streaming"""
    processor = FastTransitionProcessor()
    
    # Sample user text with rich information
    user_text = """
    Dr. Sarah Chen is a 35-year-old quantum computing researcher at MIT. 
    Her email is sarah.chen@mit.edu. She has published over 40 papers on 
    quantum algorithms and holds 3 patents. She earned her PhD from Stanford 
    in 2015 and has been leading the Quantum Systems Lab since 2020. 
    She's a verified researcher with numerous academic credentials and is 
    considered a premium member of our research community due to her 
    extensive contributions to the field.
    """
    
    # Define what happens when required fields are ready
    async def on_fast_transition(name: str, email: str, is_verified: bool):
        """Execute the next job when required fields are ready"""
        return await b.ProcessUser(name, email, is_verified)
    
    # Process the stream with fast transitions
    final_profile = await processor.process_stream(user_text, on_fast_transition)
    
    print(f"\n✨ Final extracted profile:")
    print(f"   Name: {final_profile.name}")
    print(f"   Email: {final_profile.email}")
    print(f"   Verified: {final_profile.is_verified}")
    print(f"   Premium: {final_profile.is_premium}")

if __name__ == "__main__":
    asyncio.run(main())