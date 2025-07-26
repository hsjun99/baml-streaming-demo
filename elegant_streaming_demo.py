#!/usr/bin/env python3
"""
Schema-Driven BAML Streaming Demo
=================================

Demonstrates Pydantic schema-driven BAML streaming.
Single source of truth: the Pydantic model defines both structure and execution requirements.
"""

import asyncio
import sys
from dotenv import load_dotenv

# Add baml_client to path
sys.path.insert(0, 'baml_client')
from baml_client import b

# Import our schema-driven helpers
from baml_streaming_helpers import BAMLStreamProcessor
from user_profile_schema import UserProfile

# Load environment variables
load_dotenv()


async def demo_schema_driven():
    """Demonstrate schema-driven streaming with UserProfile"""
    print("🎯 DEMO 1: Schema-Driven Streaming")
    print("=" * 50)
    
    # Single line setup - schema defines everything!
    processor = BAMLStreamProcessor(UserProfile)
    
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
    summary = await processor.process_stream(stream, on_required_ready=on_required_fields_ready)
    
    if summary.time_savings_percent:
        print(f"\n✨ Demo 1 completed with {summary.time_savings_percent:.1f}% time savings!")
    else:
        print(f"\n✨ Demo 1 completed in {summary.total_time:.3f}s!")
    return summary


async def demo_custom_components():
    """Demonstrate custom components with schema-driven approach"""
    print("\n\n🎯 DEMO 2: Custom Components")
    print("=" * 50)
    
    from baml_streaming_helpers import StreamDisplayFormatter, StreamTimer
    
    # Custom components while keeping schema-driven approach
    custom_formatter = StreamDisplayFormatter()
    custom_timer = StreamTimer()
    
    processor = BAMLStreamProcessor(
        model_class=UserProfile,
        formatter=custom_formatter,
        timer=custom_timer,
        title="Custom BAML Streaming"
    )
    
    # Define handlers for required fields and completion
    async def on_required_ready(field_states, elapsed_time):
        name = field_states["name"].value
        email = field_states["email"].value
        is_verified = field_states["is_verified"].value
        print(f"   🚀 Required fields ready: Processing verified user {name}")
        
        try:
            result = await b.ProcessUser(name, email)
            print(f"   ✅ User processed: {result}")
        except Exception as e:
            print(f"   ❌ Processing failed: {e}")
    
    async def on_all_complete(field_states, elapsed_time):
        premium = field_states["is_premium"].value
        age = field_states["age"].value
        print(f"   🎉 Complete profile processed - Age: {age}, Premium: {premium}")
    
    # Test data
    user_text = """
    Dr. Sarah Chen is a distinguished professor of Computer Science at Stanford University.
    Contact her at sarah.chen@stanford.edu. She's 42 years old and has been teaching 
    for over 15 years. Her research focuses on machine learning and she has published 
    numerous papers in top conferences. As a tenured professor with extensive publications,
    she qualifies for premium access to our research database.
    """
    
    # Process with handlers
    stream = b.stream.ExtractUserProfile(user_text)
    summary = await processor.process_stream(
        stream, 
        on_required_ready=on_required_ready,
        on_all_complete=on_all_complete
    )
    
    if summary.time_savings_percent:
        print(f"\n✨ Demo 2 completed with {summary.time_savings_percent:.1f}% time savings!")
    else:
        print(f"\n✨ Demo 2 completed in {summary.total_time:.3f}s!")
    return summary


async def demo_comparison():
    """Show the difference in code complexity"""
    print("\n\n🎯 DEMO 3: Code Complexity Comparison")
    print("=" * 50)
    
    print("""
📊 BEFORE (FieldConfig approach):
- Separate configuration classes (FieldConfig)
- Dual source of truth (schema + config)
- Manual field mapping and validation
- Complex configuration management
- More boilerplate code

✨ AFTER (Schema-driven approach):
- Single source of truth: Pydantic model
- Schema defines both structure AND execution requirements
- Automatic introspection using json_schema_extra
- Type safety built-in with Pydantic
- Clean processor = BAMLStreamProcessor(UserProfile)

🎯 KEY BENEFITS:
- Schema as configuration (single source of truth)
- Pydantic-native approach with full validation
- Zero configuration duplication
- Leverages existing Python ecosystem
- Clean, intuitive API
- Production-ready type safety
""")


async def main():
    """Run all demos"""
    print("🚀 Elegant BAML Streaming Helpers Demo")
    print("=" * 60)
    print("Demonstrating clean, reusable architecture for BAML streaming\n")
    
    try:
        # Run demos
        summary1 = await demo_schema_driven()
        summary2 = await demo_custom_components()
        await demo_comparison()
        
        # Overall summary
        print("\n\n🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        savings1 = f", {summary1.time_savings_percent:.1f}% savings" if summary1.time_savings_percent else ""
        savings2 = f", {summary2.time_savings_percent:.1f}% savings" if summary2.time_savings_percent else ""
        print(f"Demo 1 Performance: {summary1.partial_count} partials{savings1}")
        print(f"Demo 2 Performance: {summary2.partial_count} partials{savings2}")
        print("\n✨ Schema-driven BAML streaming: clean, type-safe, and production-ready!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())