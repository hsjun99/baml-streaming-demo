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


# Transition System
# =================

class TransitionCondition(ABC):
    """Abstract base class for defining when transitions should trigger"""
    
    @abstractmethod
    def is_satisfied(self, field_states: Dict[str, FieldState]) -> bool:
        """Check if this transition condition is satisfied"""
        pass
    
    @abstractmethod
    def describe(self) -> str:
        """Human-readable description of this condition"""
        pass


class RequiredFieldsComplete(TransitionCondition):
    """Triggers when all specified required fields are complete"""
    
    def __init__(self, required_fields: List[str]):
        self.required_fields = required_fields
    
    def is_satisfied(self, field_states: Dict[str, FieldState]) -> bool:
        return all(
            field_states.get(field_name, FieldState(field_name, None, FieldStatus.NONE, 0)).status == FieldStatus.COMPLETE
            for field_name in self.required_fields
        )
    
    def describe(self) -> str:
        return f"Required fields complete: {', '.join(self.required_fields)}"


class AllFieldsComplete(TransitionCondition):
    """Triggers when all fields are complete"""
    
    def is_satisfied(self, field_states: Dict[str, FieldState]) -> bool:
        return all(state.status == FieldStatus.COMPLETE for state in field_states.values())
    
    def describe(self) -> str:
        return "All fields complete"


class CustomCondition(TransitionCondition):
    """Triggers based on a custom function"""
    
    def __init__(self, condition_func: Callable[[Dict[str, FieldState]], bool], description: str = "Custom condition"):
        self.condition_func = condition_func
        self.description = description
    
    def is_satisfied(self, field_states: Dict[str, FieldState]) -> bool:
        return self.condition_func(field_states)
    
    def describe(self) -> str:
        return self.description


class TransitionManager:
    """Manages multiple transition conditions and tracks which have been triggered"""
    
    def __init__(self, conditions: List[TransitionCondition]):
        self.conditions = conditions
        self.triggered = {i: False for i in range(len(conditions))}
    
    def check_transitions(self, field_states: Dict[str, FieldState]) -> List[int]:
        """Check all conditions and return indices of newly triggered transitions"""
        newly_triggered = []
        for i, condition in enumerate(self.conditions):
            if not self.triggered[i] and condition.is_satisfied(field_states):
                self.triggered[i] = True
                newly_triggered.append(i)
        return newly_triggered
    
    def get_condition_description(self, index: int) -> str:
        """Get description of condition at given index"""
        if 0 <= index < len(self.conditions):
            return self.conditions[index].describe()
        return f"Unknown condition {index}"
    
    def reset(self):
        """Reset all triggered states"""
        self.triggered = {i: False for i in range(len(self.conditions))}


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
    
    def format_transition_trigger(self, condition_desc: str, elapsed_time: float) -> str:
        """Format transition trigger message"""
        return f"""
🚀 Transition triggered at {elapsed_time:.3f}s!
   ⏱️ Condition: {condition_desc}"""


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
    fast_transition_time: Optional[float] = None
    
    @property
    def time_savings_percent(self) -> Optional[float]:
        """Calculate time savings percentage if fast transition occurred"""
        if self.fast_transition_time is None:
            return None
        return (self.total_time - self.fast_transition_time) / self.total_time * 100
    
    def format_summary(self) -> str:
        """Format performance summary for display"""
        lines = [
            "=" * 50,
            f"✅ Streaming completed in {self.total_time:.3f}s",
            f"📊 Received {self.partial_count} partial updates"
        ]
        
        if self.fast_transition_time is not None:
            savings = self.time_savings_percent
            lines.extend([
                f"⏱️ Fast transition at {self.fast_transition_time:.3f}s",
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
        transitions: List[TransitionCondition],
        formatter: Optional[StreamDisplayFormatter] = None,
        timer: Optional[StreamTimer] = None,
        title: str = "BAML Streaming"
    ):
        self.field_configs = field_configs
        self.transition_manager = TransitionManager(transitions)
        self.formatter = formatter or StreamDisplayFormatter()
        self.timer = timer or StreamTimer()
        self.title = title
        
        # Derived properties
        self.required_fields = {name for name, config in field_configs.items() if config.required}
    
    async def process_stream(
        self,
        stream,
        transition_handlers: Optional[Dict[int, Callable[[Dict[str, FieldState], float], Any]]] = None
    ) -> PerformanceSummary:
        """Process a BAML stream with the configured behavior"""
        transition_handlers = transition_handlers or {}
        partial_count = 0
        
        # Reset state
        self.transition_manager.reset()
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
                
                # Check for transitions
                triggered_transitions = self.transition_manager.check_transitions(field_states)
                
                # Handle transitions
                for transition_idx in triggered_transitions:
                    condition_desc = self.transition_manager.get_condition_description(transition_idx)
                    self.timer.mark_event(f"transition_{transition_idx}")
                    
                    print(self.formatter.format_transition_trigger(condition_desc, elapsed))
                    
                    if transition_idx in transition_handlers:
                        await transition_handlers[transition_idx](field_states, elapsed)
                
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
            fast_transition_time = self.timer.get_event_time("transition_0")  # First transition
            summary = PerformanceSummary(
                total_time=total_time,
                partial_count=partial_count,
                events=self.timer.events.copy(),
                fast_transition_time=fast_transition_time
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
            is_required = field_name in self.required_fields
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
        
        transitions = [RequiredFieldsComplete(required)]
        
        return cls(field_configs, transitions, title=title, **kwargs)
    
    @classmethod  
    def for_fast_transitions(
        cls,
        field_configs: Dict[str, FieldConfig],
        required_fields: List[str],
        title: str = "BAML Fast Transitions",
        **kwargs
    ) -> "BAMLStreamProcessor":
        """Create a processor optimized for fast transitions (convenience method)"""
        transitions = [
            RequiredFieldsComplete(required_fields),
            AllFieldsComplete()
        ]
        
        return cls(field_configs, transitions, title=title, **kwargs)