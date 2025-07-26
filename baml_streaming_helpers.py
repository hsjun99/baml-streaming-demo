#!/usr/bin/env python3
"""
BAML Streaming Helpers
======================

Generalizable, reusable helper functions for BAML streaming operations.
Designed from the perspective of clean architecture and extensibility.

Key Design Principles:
- Separation of concerns
- Configuration-driven behavior
- Composability and reusability
- Type safety and easy testing
- Simple common case, extensible for power users
"""

import time
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union


# Core Data Structures
# ====================

class FieldStatus(Enum):
    """Status of a field during streaming"""
    NONE = "none"        # Field not present yet
    COMPLETE = "Complete"  # Field has a value


@dataclass(frozen=True, slots=True)
class FieldState:
    """Immutable representation of a field's state during streaming"""
    name: str
    value: Any
    status: FieldStatus
    timestamp: float


@dataclass(frozen=True)
class FieldConfig:
    """Configuration for how a field should be processed and displayed"""
    name: str
    required: bool = False
    display_name: Optional[str] = None
    formatter: Optional[Callable[[Any], str]] = None
    
    @property
    def effective_display_name(self) -> str:
        return self.display_name or self.name


# Required Field System
# =====================

class RequiredFieldsChecker:
    """Manages checking when required fields are ready"""
    
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields
        self.required_ready_triggered = False
        self.all_complete_triggered = False
    
    def check_required_ready(self, field_states: Dict[str, FieldState]) -> bool:
        """Check if required fields are ready (and not already triggered)"""
        if self.required_ready_triggered:
            return False
            
        required_ready = all(
            field_states.get(field_name, FieldState(field_name, None, FieldStatus.NONE, 0)).status == FieldStatus.COMPLETE
            for field_name in self.required_fields
        )
        
        if required_ready:
            self.required_ready_triggered = True
            return True
        return False
    
    def check_all_complete(self, field_states: Dict[str, FieldState]) -> bool:
        """Check if all fields are complete (and not already triggered)"""
        if self.all_complete_triggered:
            return False
            
        all_complete = all(state.status == FieldStatus.COMPLETE for state in field_states.values())
        
        if all_complete:
            self.all_complete_triggered = True
            return True
        return False
    
    def reset(self):
        """Reset all triggered states"""
        self.required_ready_triggered = False
        self.all_complete_triggered = False
    
    def get_required_fields_description(self) -> str:
        """Get description of required fields"""
        return f"Required fields: {', '.join(self.required_fields)}"


# Display and Formatting
# ======================

class StreamDisplayFormatter:
    """Handles display formatting for streaming progress"""
    
    def format_field_line(self, field_state: FieldState, config: FieldConfig, is_required: bool) -> str:
        """Format a single field line for display"""
        marker = "⭐" if is_required else "  "
        emoji = "✅" if field_state.status == FieldStatus.COMPLETE else "⏸️"
        
        value_str = self._format_value(field_state.value, config)
        display_name = config.effective_display_name
        
        return f"{marker} {display_name:10}: {emoji} {field_state.status.value:10} → {value_str}"
    
    def _format_value(self, value: Any, config: FieldConfig) -> str:
        """Format a field value for display"""
        if config.formatter:
            return config.formatter(value)
        
        if value is None:
            return "[None]"
        elif isinstance(value, str) and len(value) > 30:
            return f'"{value[:27]}..."'
        else:
            return str(value)
    
    def format_header(self, title: str, field_count: int, required_count: int) -> str:
        """Format the header for streaming display"""
        return f"""🚀 {title}
{'=' * 60}
{field_count} fields tracked, {required_count} required for fast transition
"""
    
    def format_partial_header(self, partial_count: int, elapsed_time: float) -> str:
        """Format header for each partial update"""
        return f"\n📊 Partial #{partial_count} at {elapsed_time:.3f}s:"
    
    def format_required_ready(self, required_fields: List[str], elapsed_time: float) -> str:
        """Format required fields ready message"""
        return f"""
🚀 Required fields ready at {elapsed_time:.3f}s!
   ⏱️ Fields: {', '.join(required_fields)}"""
    
    def format_all_complete(self, elapsed_time: float) -> str:
        """Format all fields complete message"""
        return f"""
✅ All fields complete at {elapsed_time:.3f}s!"""


# Performance Tracking
# ====================

@dataclass
class StreamTimer:
    """Tracks timing and performance metrics for streaming"""
    start_time: float = field(default_factory=time.time)
    events: Dict[str, float] = field(default_factory=dict)
    
    def get_elapsed(self) -> float:
        """Get elapsed time since start"""
        return time.time() - self.start_time
    
    def mark_event(self, event_name: str) -> float:
        """Mark an event and return the timestamp"""
        elapsed = self.get_elapsed()
        self.events[event_name] = elapsed
        return elapsed
    
    def get_event_time(self, event_name: str) -> Optional[float]:
        """Get the time when an event occurred"""
        return self.events.get(event_name)
    
    def reset(self):
        """Reset the timer"""
        self.start_time = time.time()
        self.events.clear()


@dataclass
class PerformanceSummary:
    """Summary of streaming performance metrics"""
    total_time: float
    partial_count: int
    events: Dict[str, float]
    required_ready_time: Optional[float] = None
    
    @property
    def time_savings_percent(self) -> Optional[float]:
        """Calculate time savings percentage if required fields triggered early"""
        if self.required_ready_time is None:
            return None
        return (self.total_time - self.required_ready_time) / self.total_time * 100
    
    def format_summary(self) -> str:
        """Format performance summary for display"""
        lines = [
            "=" * 50,
            f"✅ Streaming completed in {self.total_time:.3f}s",
            f"📊 Received {self.partial_count} partial updates"
        ]
        
        if self.required_ready_time is not None:
            savings = self.time_savings_percent
            lines.extend([
                f"⏱️ Required fields ready at {self.required_ready_time:.3f}s",
                f"   Time savings: {savings:.1f}% of total execution"
            ])
        
        return "\n".join(lines)


# Main Orchestrator
# =================

class BAMLStreamProcessor:
    """Main orchestrator for BAML streaming with configurable behavior"""
    
    def __init__(
        self,
        field_configs: Dict[str, FieldConfig],
        formatter: Optional[StreamDisplayFormatter] = None,
        timer: Optional[StreamTimer] = None,
        title: str = "BAML Streaming"
    ):
        self.field_configs = field_configs
        self.formatter = formatter or StreamDisplayFormatter()
        self.timer = timer or StreamTimer()
        self.title = title
        
        # Derived properties
        self.required_fields = [name for name, config in field_configs.items() if config.required]
        self.required_checker = RequiredFieldsChecker(self.required_fields)
    
    async def process_stream(
        self,
        stream,
        on_required_ready: Optional[Callable[[Dict[str, FieldState], float], Any]] = None,
        on_all_complete: Optional[Callable[[Dict[str, FieldState], float], Any]] = None
    ) -> PerformanceSummary:
        """Process a BAML stream with the configured behavior"""
        partial_count = 0
        
        # Reset state
        self.required_checker.reset()
        self.timer.reset()
        
        # Display header
        print(self.formatter.format_header(
            self.title,
            len(self.field_configs),
            len(self.required_fields)
        ))
        
        # Process stream
        try:
            async for partial in stream:
                partial_count += 1
                elapsed = self.timer.get_elapsed()
                
                # Extract field states
                field_states = self._extract_all_field_states(partial)
                
                # Check if required fields are ready
                if self.required_checker.check_required_ready(field_states):
                    self.timer.mark_event("required_ready")
                    print(self.formatter.format_required_ready(self.required_fields, elapsed))
                    
                    if on_required_ready:
                        await on_required_ready(field_states, elapsed)
                
                # Check if all fields are complete
                if self.required_checker.check_all_complete(field_states):
                    self.timer.mark_event("all_complete")
                    print(self.formatter.format_all_complete(elapsed))
                    
                    if on_all_complete:
                        await on_all_complete(field_states, elapsed)
                
                # Display current state
                self._display_partial_update(partial_count, elapsed, field_states)
                
        except Exception as e:
            print(f"❌ Stream error: {e}")
            raise
        
        # Get final result
        try:
            final_result = await stream.get_final_response()
            total_time = self.timer.get_elapsed()
            
            # Generate performance summary
            required_ready_time = self.timer.get_event_time("required_ready")
            summary = PerformanceSummary(
                total_time=total_time,
                partial_count=partial_count,
                events=self.timer.events.copy(),
                required_ready_time=required_ready_time
            )
            
            print("\n" + summary.format_summary())
            return summary
            
        except Exception as e:
            print(f"❌ Final response error: {e}")
            raise
    
    def _extract_all_field_states(self, partial) -> Dict[str, FieldState]:
        """Extract field states from a partial update"""
        field_states = {}
        current_time = time.time()
        
        for field_name, config in self.field_configs.items():
            field_obj = getattr(partial, field_name, None)
            
            if field_obj is None:
                state = FieldState(field_name, None, FieldStatus.NONE, current_time)
            else:
                state = FieldState(field_name, field_obj, FieldStatus.COMPLETE, current_time)
            
            field_states[field_name] = state
        
        return field_states
    
    def _display_partial_update(self, partial_count: int, elapsed: float, field_states: Dict[str, FieldState]):
        """Display the current state of all fields"""
        print(self.formatter.format_partial_header(partial_count, elapsed))
        
        for field_name, config in self.field_configs.items():
            field_state = field_states[field_name]
            is_required = config.required
            line = self.formatter.format_field_line(field_state, config, is_required)
            print(line)
    
    @classmethod
    def from_fields(
        cls,
        fields: List[str],
        required: List[str],
        title: str = "BAML Streaming",
        **kwargs
    ) -> "BAMLStreamProcessor":
        """Create a processor from simple field lists (convenience method)"""
        field_configs = {
            field_name: FieldConfig(field_name, required=(field_name in required))
            for field_name in fields
        }
        
        return cls(field_configs, title=title, **kwargs)