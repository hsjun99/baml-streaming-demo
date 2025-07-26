#!/usr/bin/env python3
"""
Elegant BAML Streaming Demo
===========================

Demonstrates the new generalizable BAML streaming helpers.
Shows how complex streaming logic becomes simple and readable.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Add baml_client to path
sys.path.insert(0, 'baml_client')
from baml_client import b

# Import our elegant helpers
from baml_streaming_helpers import (
    BAMLStreamProcessor,
    FieldConfig,
    RequiredFieldsComplete,
    AllFieldsComplete,
    CustomCondition
)

# Load environment variables
load_dotenv()


async def demo_simple_usage():
    """Demonstrate the simplest possible usage"""
    print("🎯 DEMO 1: Super Simple Usage")
    print("=" * 50)
    
    # Create processor with minimal configuration
    processor = BAMLStreamProcessor.from_fields(
        fields=["name", "email", "is_verified", "bio", "age", "is_premium"],
        required=["name", "email", "is_verified"],
        title="Simple BAML Streaming"
    )
    
    # Define what to do when required fields are ready
    async def on_required_fields_ready(field_states, elapsed_time):
        name = field_states["name"].value
        email = field_states["email"].value
        print(f"   🚀 Starting ProcessUser({name}, {email})")
        
        try:
            result = await b.ProcessUser(name, email)
            print(f"   ✅ ProcessUser completed: {result}")
        except Exception as e:
            print(f"   ❌ ProcessUser failed: {e}")
    
    # Test data
    user_text = """
    Dr. Sarah Chen is a distinguished professor of Computer Science at Stanford University.
    Contact her at sarah.chen@stanford.edu. She's 42 years old and has been teaching 
    for over 15 years. Her research focuses on machine learning and she has published 
    numerous papers in top conferences. As a tenured professor with extensive publications,
    she qualifies for premium access to our research database.
    """
    
    # Process the stream - that's it!
    stream = b.stream.ExtractUserProfile(user_text)
    summary = await processor.process_stream(stream, {0: on_required_fields_ready})
    
    print(f"\n✨ Demo 1 completed with {summary.time_savings_percent:.1f}% time savings!")
    return summary


async def demo_advanced_usage():
    """Demonstrate advanced configuration options"""
    print("\n\n🎯 DEMO 2: Advanced Configuration")
    print("=" * 50)
    
    # Create processor with custom configurations
    field_configs = {
        "name": FieldConfig("name", required=True, display_name="Full Name"),
        "email": FieldConfig("email", required=True, display_name="Email Address", 
                           formatter=lambda x: f"📧 {x}" if x else "[None]"),
        "is_verified": FieldConfig("is_verified", required=True, display_name="Verified",
                                 formatter=lambda x: "✅ Yes" if x else "❌ No" if x is not None else "[None]"),
        "bio": FieldConfig("bio", display_name="Biography",
                         formatter=lambda x: f'"{x[:50]}..."' if x and len(x) > 50 else str(x)),
        "age": FieldConfig("age", display_name="Age",
                         formatter=lambda x: f"{x} years old" if x else "[None]"),
        "is_premium": FieldConfig("is_premium", display_name="Premium Status",
                                formatter=lambda x: "🌟 Premium" if x else "📦 Standard" if x is not None else "[None]")
    }
    
    # Create multiple transition conditions
    transitions = [
        RequiredFieldsComplete(["name", "email", "is_verified"]),  # Fast transition
        CustomCondition(
            lambda states: states["age"].value and states["age"].value >= 21,
            "User is 21 or older"
        ),
        AllFieldsComplete()  # Everything done
    ]
    
    processor = BAMLStreamProcessor(
        field_configs=field_configs,
        transitions=transitions,
        title="Advanced BAML Processing"
    )
    
    # Define handlers for different transitions
    async def on_fast_transition(field_states, elapsed_time):
        name = field_states["name"].value
        email = field_states["email"].value
        is_verified = field_states["is_verified"].value
        print(f"   🚀 Fast transition: Processing verified user {name}")
        
        try:
            result = await b.ProcessUser(name, email)
            print(f"   ✅ User processed: {result}")
        except Exception as e:
            print(f"   ❌ Processing failed: {e}")
    
    async def on_age_verified(field_states, elapsed_time):
        age = field_states["age"].value
        print(f"   🔞 Age verification passed: User is {age} years old")
    
    async def on_all_complete(field_states, elapsed_time):
        premium = field_states["is_premium"].value
        print(f"   🎉 Complete profile processed - Premium: {premium}")
    
    # Test data
    user_text = """
    Dr. Sarah Chen is a distinguished professor of Computer Science at Stanford University.
    Contact her at sarah.chen@stanford.edu. She's 42 years old and has been teaching 
    for over 15 years. Her research focuses on machine learning and she has published 
    numerous papers in top conferences. As a tenured professor with extensive publications,
    she qualifies for premium access to our research database.
    """
    
    # Process with multiple handlers
    transition_handlers = {
        0: on_fast_transition,    # Required fields complete
        1: on_age_verified,       # Age >= 21
        2: on_all_complete        # All fields complete
    }
    
    stream = b.stream.ExtractUserProfile(user_text)
    summary = await processor.process_stream(stream, transition_handlers)
    
    print(f"\n✨ Demo 2 completed with {summary.time_savings_percent:.1f}% time savings!")
    return summary


async def demo_comparison():
    """Show the difference in code complexity"""
    print("\n\n🎯 DEMO 3: Code Complexity Comparison")
    print("=" * 50)
    
    print("""
📊 BEFORE (original implementation):
- 150+ lines of mixed logic
- Hardcoded field names and configurations
- Manual state tracking and display formatting
- Difficult to extend or modify
- Single-use, not reusable

✨ AFTER (with helpers):
- 10-20 lines for typical use case
- Declarative configuration
- Automatic state management
- Easy to extend and customize
- Highly reusable across projects

🎯 KEY BENEFITS:
- 90% reduction in boilerplate code
- Separation of concerns (config vs logic vs display)
- Type-safe configuration
- Easy testing of individual components
- Composable design for complex scenarios
- Clean APIs that are hard to misuse
""")


async def main():
    """Run all demos"""
    print("🚀 Elegant BAML Streaming Helpers Demo")
    print("=" * 60)
    print("Demonstrating clean, reusable architecture for BAML streaming\n")
    
    try:
        # Run demos
        summary1 = await demo_simple_usage()
        summary2 = await demo_advanced_usage()
        await demo_comparison()
        
        # Overall summary
        print("\n\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Demo 1 Performance: {summary1.partial_count} partials, {summary1.time_savings_percent:.1f}% savings")
        print(f"Demo 2 Performance: {summary2.partial_count} partials, {summary2.time_savings_percent:.1f}% savings")
        print("\n✨ The new helpers provide clean, elegant, and reusable BAML streaming!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())