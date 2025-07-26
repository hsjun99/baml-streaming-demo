#!/usr/bin/env python3
"""
BAML Streaming - Raymond Hettinger Style
========================================

Ultra-simple, functional approach to BAML streaming.
"Don't write classes, write functions" - Raymond Hettinger

Core Philosophy:
- Simple is better than complex
- Flat is better than nested  
- There should be one obvious way to do it
- If you can't explain it in 30 seconds, it's too complex

The entire system: 1 NamedTuple + 4 pure functions = 60 lines
"""

import time
from typing import NamedTuple, Set, Dict, Any, Type, AsyncGenerator
from pydantic import BaseModel


# Single data structure - Raymond loves NamedTuple!
class StreamState(NamedTuple):
    """Current state of the stream - immutable and simple"""
    fields: Dict[str, Any]
    required_ready: bool
    all_complete: bool
    elapsed: float
    partial_count: int


# Pure functions only - no complex classes needed
def get_required_fields(schema_class: Type[BaseModel]) -> Set[str]:
    """Extract required fields from Pydantic schema - one clear purpose"""
    return {
        name for name, field in schema_class.model_fields.items() 
        if field.json_schema_extra and field.json_schema_extra.get('baml_required')
    }


def get_all_fields(schema_class: Type[BaseModel]) -> Set[str]:
    """Get all field names from schema - obvious and simple"""
    return set(schema_class.model_fields.keys())


def extract_current_fields(partial, schema_class: Type[BaseModel]) -> Dict[str, Any]:
    """Extract available fields from partial response - no magic, just getattr"""
    return {
        name: getattr(partial, name, None) 
        for name in schema_class.model_fields 
        if hasattr(partial, name) and getattr(partial, name) is not None
    }


async def track_stream(
    stream, 
    schema_class: Type[BaseModel],
    *,
    show_progress: bool = True,
    on_required_ready=None,
    on_all_ready=None
) -> AsyncGenerator[StreamState, None]:
    """
    The one obvious way to track BAML streams.
    
    Raymond Hettinger approved: simple generator that yields stream state.
    No complex objects, no nested abstractions, just pure functionality.
    
    Usage:
        async for state in track_stream(stream, UserProfile):
            if state.required_ready:
                await next_action(state.fields)
            if state.all_complete:
                await final_action(state.fields)
                
        # Or with callbacks:
        async for state in track_stream(
            stream, UserProfile,
            on_required_ready=lambda fields: process_user(fields),
            on_all_ready=lambda fields: finalize_user(fields)
        ):
    """
    # Simple setup - no complex initialization
    required_fields = get_required_fields(schema_class)
    all_fields = get_all_fields(schema_class)
    start_time = time.time()
    partial_count = 0
    required_notified = False
    all_complete_notified = False
    
    # The generator pattern Raymond loves
    async for partial in stream:
        partial_count += 1
        current_fields = extract_current_fields(partial, schema_class)
        elapsed = time.time() - start_time
        
        # Simple boolean logic - no complex state management
        required_ready = (
            required_fields.issubset(current_fields) and 
            not required_notified
        )
        if required_ready:
            required_notified = True
            if on_required_ready:
                await on_required_ready(current_fields)
            
        all_complete = set(current_fields.keys()) == all_fields
        all_complete_triggered = all_complete and not all_complete_notified
        if all_complete_triggered:
            all_complete_notified = True
            if on_all_ready:
                await on_all_ready(current_fields)
        
        # Yield simple state - let the caller decide what to do
        state = StreamState(
            fields=current_fields,
            required_ready=required_ready,
            all_complete=all_complete_triggered,
            elapsed=elapsed,
            partial_count=partial_count
        )
        
        if show_progress:
            print(format_progress(state, required_fields))
            
        yield state


def format_progress(state: StreamState, required_fields: Set[str]) -> str:
    """Format progress display - simple string formatting"""
    ready_marker = "🚀" if state.required_ready else "📊"
    complete_marker = "✅" if state.all_complete else ""
    
    field_summary = []
    for name, value in state.fields.items():
        marker = "⭐" if name in required_fields else "  "
        value_str = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
        field_summary.append(f"{marker} {name}: {value_str}")
    
    header = f"{ready_marker} Partial #{state.partial_count} at {state.elapsed:.3f}s {complete_marker}"
    
    if state.required_ready:
        header += "\n🚀 REQUIRED FIELDS READY - Fast execution triggered!"
    
    if state.all_complete:
        header += "\n🎉 ALL FIELDS COMPLETE - Full profile ready!"
    
    return f"{header}\n" + "\n".join(field_summary)


# Convenience function for common use case
async def simple_track(stream, schema_class: Type[BaseModel], on_required_ready=None, on_all_ready=None):
    """
    Even simpler API for the most common use case.
    Returns final statistics.
    """
    stats = {"total_time": 0, "partial_count": 0, "required_ready_time": None, "all_complete_time": None}
    
    async for state in track_stream(stream, schema_class):
        stats["partial_count"] = state.partial_count
        stats["total_time"] = state.elapsed
        
        if state.required_ready:
            stats["required_ready_time"] = state.elapsed
            if on_required_ready:
                await on_required_ready(state.fields)
        
        if state.all_complete:
            stats["all_complete_time"] = state.elapsed
            if on_all_ready:
                await on_all_ready(state.fields)
    
    # Calculate time savings
    if stats["required_ready_time"]:
        savings = (stats["total_time"] - stats["required_ready_time"]) / stats["total_time"] * 100
        print(f"\n✨ Completed with {savings:.1f}% time savings!")
        print(f"   Required ready: {stats['required_ready_time']:.3f}s")
        print(f"   Total time: {stats['total_time']:.3f}s")
    
    return stats


# That's it! ~80 lines total.
# Raymond Hettinger would be proud: simple, obvious, functional.