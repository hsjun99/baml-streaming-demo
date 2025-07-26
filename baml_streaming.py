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
from typing import NamedTuple, Set, Dict, Any, Type, AsyncGenerator, Optional
from pydantic import BaseModel


# Single data structure - Raymond loves NamedTuple!
class StreamState(NamedTuple):
    """Current state of the stream - immutable and simple"""
    fields: Dict[str, Any]
    required_ready: bool
    all_complete: bool
    elapsed: float
    partial_count: int


class StreamStats(NamedTuple):
    """Final performance statistics - Raymond Hettinger approved immutable data"""
    total_time: float
    partial_count: int
    required_ready_time: Optional[float] = None
    all_complete_time: Optional[float] = None
    
    @property
    def time_savings_percent(self) -> Optional[float]:
        """Calculate time savings percentage if required fields triggered early"""
        if self.required_ready_time is None:
            return None
        return (self.total_time - self.required_ready_time) / self.total_time * 100


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
    """Extract available fields from partial response - David Beazley optimized"""
    fields = {}
    for name in schema_class.model_fields:
        if hasattr(partial, name):
            value = getattr(partial, name)
            if value is not None:
                fields[name] = value
    return fields


def notification_tracker():
    """David Beazley style: functional state tracking with closure"""
    notified = set()
    
    def is_new_event(event_type: str) -> bool:
        if event_type not in notified:
            notified.add(event_type)
            return True
        return False
    
    return is_new_event


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
    # Simple setup - functional state tracking
    required_fields = get_required_fields(schema_class)
    all_fields = get_all_fields(schema_class)
    start_time = time.time()
    partial_count = 0
    
    # David Beazley style: functional state tracking
    track_notifications = notification_tracker()
    
    # The generator pattern Raymond loves
    async for partial in stream:
        partial_count += 1
        current_fields = extract_current_fields(partial, schema_class)
        elapsed = time.time() - start_time
        
        # Functional event tracking - David Beazley approved
        required_ready = (
            required_fields.issubset(current_fields) and 
            track_notifications("required_ready")
        )
        if required_ready and on_required_ready:
            await on_required_ready(current_fields)
            
        all_complete_triggered = (
            set(current_fields.keys()) == all_fields and
            track_notifications("all_complete")
        )
        if all_complete_triggered and on_all_ready:
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


def format_field_line(name: str, value: Any, is_required: bool) -> str:
    """Format a single field line - David Beazley single responsibility"""
    marker = "⭐" if is_required else "  "
    value_str = str(value)[:20] + "..." if len(str(value)) > 20 else str(value)
    return f"{marker} {name}: {value_str}"


def format_header(state: StreamState) -> str:
    """Format the progress header with state indicators"""
    ready_marker = "🚀" if state.required_ready else "📊"
    complete_marker = "✅" if state.all_complete else ""
    
    header = f"{ready_marker} Partial #{state.partial_count} at {state.elapsed:.3f}s {complete_marker}"
    
    if state.required_ready:
        header += "\n🚀 REQUIRED FIELDS READY - Fast execution triggered!"
    
    if state.all_complete:
        header += "\n🎉 ALL FIELDS COMPLETE - Full profile ready!"
    
    return header


def format_progress(state: StreamState, required_fields: Set[str]) -> str:
    """Format progress display - composed from smaller functions"""
    header = format_header(state)
    field_lines = [
        format_field_line(name, value, name in required_fields)
        for name, value in state.fields.items()
    ]
    return f"{header}\n" + "\n".join(field_lines)


# Convenience function for common use case
async def simple_track(stream, schema_class: Type[BaseModel], on_required_ready=None, on_all_ready=None) -> StreamStats:
    """
    Even simpler API for the most common use case.
    Returns final statistics as immutable NamedTuple.
    """
    # Track state with local variables
    total_time = 0.0
    partial_count = 0
    required_ready_time = None
    all_complete_time = None
    
    async for state in track_stream(stream, schema_class):
        partial_count = state.partial_count
        total_time = state.elapsed
        
        if state.required_ready:
            required_ready_time = state.elapsed
            if on_required_ready:
                await on_required_ready(state.fields)
        
        if state.all_complete:
            all_complete_time = state.elapsed
            if on_all_ready:
                await on_all_ready(state.fields)
    
    # Create immutable stats
    stats = StreamStats(
        total_time=total_time,
        partial_count=partial_count,
        required_ready_time=required_ready_time,
        all_complete_time=all_complete_time
    )
    
    # Display results using the NamedTuple's property
    if stats.time_savings_percent:
        print(f"\n✨ Completed with {stats.time_savings_percent:.1f}% time savings!")
        print(f"   Required ready: {stats.required_ready_time:.3f}s")
        print(f"   Total time: {stats.total_time:.3f}s")
    
    return stats


# That's it! ~80 lines total.
# Raymond Hettinger would be proud: simple, obvious, functional.