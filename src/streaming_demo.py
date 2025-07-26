import asyncio
from typing import Optional, Any, Callable
from dataclasses import dataclass
from baml_client.baml_client.async_client import b
from baml_client.baml_client.types import UserProfile
from baml_client.baml_client.stream_types import StreamState, UserProfile as StreamingUserProfile


@dataclass
class UserProfileState:
    """State container for UserProfile fields with streaming updates"""
    name: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[StreamState[str]] = None
    age: Optional[StreamState[int]] = None
    
    # Track which fields have been completed
    name_complete: bool = False
    email_complete: bool = False
    bio_complete: bool = False
    age_complete: bool = False
    
    # Callbacks for field updates
    on_field_update: Optional[Callable[[str, Any], None]] = None
    on_ready_for_next_job: Optional[Callable[[], None]] = None
    
    def update_field(self, field_name: str, value: Any, is_complete: bool = False):
        """Update a field and trigger callbacks if necessary"""
        setattr(self, field_name, value)
        setattr(self, f"{field_name}_complete", is_complete)
        
        if self.on_field_update:
            self.on_field_update(field_name, value)
        
        # Check if we have the minimum required fields for next job
        if self.has_required_fields() and self.on_ready_for_next_job:
            # Schedule the async callback
            import asyncio
            asyncio.create_task(self.on_ready_for_next_job())
    
    def has_required_fields(self) -> bool:
        """Check if we have the two required fields (name and email) completed"""
        return (self.name_complete and self.email_complete and 
                self.name is not None and self.email is not None)
    
    def is_complete(self) -> bool:
        """Check if all fields are complete"""
        return all([
            self.name_complete,
            self.email_complete,
            self.bio_complete,
            self.age_complete
        ])


class StreamingProcessor:
    """Handles streaming BAML responses and state management"""
    
    def __init__(self):
        self.state = UserProfileState()
        self.next_job_triggered = False
        self.welcome_message = None
    
    async def process_user_input(self, user_text: str):
        """Process user input with streaming and fast transitions"""
        print(f"Processing user input: {user_text}")
        print("=" * 50)
        
        # Set up callbacks
        self.state.on_field_update = self._on_field_update
        self.state.on_ready_for_next_job = self._on_ready_for_next_job
        
        # Start streaming the profile extraction
        stream = b.stream.ExtractUserProfile(user_text)
        
        try:
            async for partial in stream:
                await self._process_partial_response(partial)
        except Exception as e:
            print(f"⚠️  Stream processing completed with validation issue: {e}")
            print("   This is expected when LLM output doesn't perfectly match streaming schema")
        
        # Get final response
        final = await stream.get_final_response()
        await self._process_final_response(final)
        
        return self.state, self.welcome_message
    
    async def _process_partial_response(self, partial: Any):
        """Process each partial streaming response"""
        print(f"🔄 Partial update received:")
        
        # Handle mixed types: name/email are plain strings, bio/age have StreamState
        if hasattr(partial, 'name') and partial.name is not None:
            # Name has @stream.done so it appears complete
            self.state.update_field('name', partial.name, is_complete=True)
            print(f"  ✅ Name (Complete): {partial.name}")
        
        if hasattr(partial, 'email') and partial.email is not None:
            # Email has @stream.done so it appears complete
            self.state.update_field('email', partial.email, is_complete=True)
            print(f"  ✅ Email (Complete): {partial.email}")
        
        if hasattr(partial, 'bio') and partial.bio is not None:
            if hasattr(partial.bio, 'state'):
                # StreamState object
                self.state.update_field('bio', partial.bio, is_complete=(partial.bio.state == "Complete"))
                bio_value = partial.bio.value if partial.bio.value else ""
                state_emoji = "✅" if partial.bio.state == "Complete" else "🔄"
                print(f"  {state_emoji} Bio ({partial.bio.state}): {bio_value[:50]}{'...' if len(str(bio_value)) > 50 else ''}")
            else:
                # Plain value - convert to StreamState
                bio_state = StreamState(value=partial.bio, state="Complete")
                self.state.update_field('bio', bio_state, is_complete=True)
                print(f"  ✅ Bio (Complete): {partial.bio[:50]}{'...' if len(str(partial.bio)) > 50 else ''}")
        
        if hasattr(partial, 'age') and partial.age is not None:
            if hasattr(partial.age, 'state'):
                # StreamState object
                self.state.update_field('age', partial.age, is_complete=(partial.age.state == "Complete"))
                age_value = partial.age.value if partial.age.value else "Unknown"
                state_emoji = "✅" if partial.age.state == "Complete" else "🔄"
                print(f"  {state_emoji} Age ({partial.age.state}): {age_value}")
            else:
                # Plain value - convert to StreamState
                age_state = StreamState(value=partial.age, state="Complete")
                self.state.update_field('age', age_state, is_complete=True)
                print(f"  ✅ Age (Complete): {partial.age}")
        elif hasattr(partial, 'age'):
            # Age field exists but is None or empty, create pending state
            age_state = StreamState(value=None, state="Pending")
            self.state.update_field('age', age_state, is_complete=False)
            print(f"  🔄 Age (Pending): Unknown")
        
        print()
    
    async def _process_final_response(self, final: UserProfile):
        """Process the final complete response"""
        print(f"🏁 Final response received:")
        print(f"  Name: {final.name}")
        print(f"  Email: {final.email}")
        print(f"  Bio: {final.bio}")
        print(f"  Age: {final.age}")
        
        # Update our internal state with final values
        if final.name:
            self.state.update_field('name', final.name, is_complete=True)
        if final.email:
            self.state.update_field('email', final.email, is_complete=True)
        if final.bio:
            bio_state = StreamState(value=final.bio, state="Complete")
            self.state.update_field('bio', bio_state, is_complete=True)
        if final.age:
            age_state = StreamState(value=final.age, state="Complete")
            self.state.update_field('age', age_state, is_complete=True)
        
        print("=" * 50)
    
    def _on_field_update(self, field_name: str, value: Any):
        """Callback for field updates"""
        # print(f"🔔 Field updated: {field_name} = {value}")
        pass
    
    async def _on_ready_for_next_job(self):
        """Callback when required fields are ready - trigger next job"""
        if not self.next_job_triggered and self.state.has_required_fields():
            self.next_job_triggered = True
            print("🚀 FAST TRANSITION: Required fields ready! Triggering next job...")
            print(f"   Name: {self.state.name}")
            print(f"   Email: {self.state.email}")
            print()
            
            # Run the next job asynchronously
            try:
                name_val = self.state.name if self.state.name else ""
                email_val = self.state.email if self.state.email else ""
                self.welcome_message = await b.ProcessUser(name_val, email_val)
                print(f"💬 Welcome message generated: {self.welcome_message}")
                print()
            except Exception as e:
                print(f"❌ Error generating welcome message: {e}")


async def demo():
    """Main demo function"""
    processor = StreamingProcessor()
    
    # Sample user input
    user_input = """
    Hi there! My name is Alice Johnson and you can reach me at alice.johnson@email.com. 
    I'm a 28-year-old software engineer who loves building AI applications. 
    I have 5 years of experience in Python and machine learning.
    """
    
    print("🎯 BAML Streaming Demo: Fast Transitions")
    print("=" * 60)
    print("Scenario: Extract user profile and trigger next job as soon as name + email are available")
    print()
    
    # Process the input
    final_state, welcome_msg = await processor.process_user_input(user_input)
    
    print("📊 Final Results:")
    print(f"  State complete: {final_state.is_complete()}")
    print(f"  Required fields ready: {final_state.has_required_fields()}")
    print(f"  Next job triggered: {processor.next_job_triggered}")
    print(f"  Welcome message: {welcome_msg}")


if __name__ == "__main__":
    # You need to set OPENAI_API_KEY environment variable
    asyncio.run(demo())