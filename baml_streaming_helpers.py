#!/usr/bin/env python3
"""
BAML Streaming Helpers
======================

Pydantic schema-driven streaming helpers for BAML operations.
Uses the Pydantic model itself as the configuration source.

Key Design Principles:
- Schema as configuration (single source of truth)
- Pydantic-native approach
- Type safety and validation
- Simple, clean API
"""

import time
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Type
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Core Data Structures
# ====================

class FieldStatus(Enum):
    """Status of a field during streaming"""
    NONE = "none"        # Field not present yet
    COMPLETE = "Complete"  # Field has a value


class FieldState(BaseModel):
    """Immutable representation of a field's state during streaming"""
    model_config = ConfigDict(frozen=True, extra='forbid')
    
    name: str
    value: Any
    status: FieldStatus
    timestamp: float = Field(default_factory=time.time)
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        if v < 0:
            raise ValueError('Timestamp must be non-negative')
        return v


# Schema Introspection
# ====================

class SchemaIntrospector:
    """Introspects Pydantic models to extract streaming configuration"""
    
    @staticmethod
    def get_required_fields(model_class: Type[BaseModel]) -> List[str]:
        """Extract fields marked as required for execution from Pydantic model"""
        required_fields = []
        
        for field_name, field_info in model_class.model_fields.items():
            # Check if field is marked as required for execution
            json_schema_extra = getattr(field_info, 'json_schema_extra', None) or {}
            if json_schema_extra.get('required_for_execution', False):
                required_fields.append(field_name)
        
        return required_fields
    
    @staticmethod
    def get_all_field_names(model_class: Type[BaseModel]) -> List[str]:
        """Get all field names from Pydantic model"""
        return list(model_class.model_fields.keys())
    
    @staticmethod
    def get_field_display_name(model_class: Type[BaseModel], field_name: str) -> str:
        """Get display name for a field (from description or field name)"""
        field_info = model_class.model_fields.get(field_name)
        if field_info and field_info.description:
            return field_info.description
        return field_name


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
            field_states.get(field_name, FieldState(name=field_name, value=None, status=FieldStatus.NONE, timestamp=0)).status == FieldStatus.COMPLETE
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
    
    def format_field_line(self, field_state: FieldState, display_name: str, is_required: bool) -> str:
        """Format a single field line for display"""
        marker = "⭐" if is_required else "  "
        emoji = "✅" if field_state.status == FieldStatus.COMPLETE else "⏸️"
        
        value_str = self._format_value(field_state.value)
        
        return f"{marker} {display_name:10}: {emoji} {field_state.status.value:10} → {value_str}"
    
    def _format_value(self, value: Any) -> str:
        """Format a field value for display"""
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

class StreamTimer(BaseModel):
    """Tracks timing and performance metrics for streaming"""
    model_config = ConfigDict(extra='forbid')
    
    start_time: float = Field(default_factory=time.time)
    events: Dict[str, float] = Field(default_factory=dict)
    
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


class PerformanceSummary(BaseModel):
    """Summary of streaming performance metrics"""
    model_config = ConfigDict(extra='forbid')
    
    total_time: float = Field(..., ge=0, description="Total execution time")
    partial_count: int = Field(..., ge=0, description="Number of partial updates received")
    events: Dict[str, float] = Field(default_factory=dict, description="Timing events")
    required_ready_time: Optional[float] = Field(default=None, ge=0, description="Time when required fields were ready")
    
    @field_validator('total_time', 'required_ready_time')
    @classmethod
    def validate_timing(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError('Time values must be non-negative')
        return v
    
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
    """Schema-driven BAML streaming processor using Pydantic models"""
    
    def __init__(
        self,
        model_class: Type[BaseModel],
        formatter: Optional[StreamDisplayFormatter] = None,
        timer: Optional[StreamTimer] = None,
        title: Optional[str] = None
    ):
        self.model_class = model_class
        self.formatter = formatter or StreamDisplayFormatter()
        self.timer = timer or StreamTimer()
        self.title = title or f"{model_class.__name__} Streaming"
        
        # Extract configuration from Pydantic model
        self.introspector = SchemaIntrospector()
        self.all_fields = self.introspector.get_all_field_names(model_class)
        self.required_fields = self.introspector.get_required_fields(model_class)
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
            len(self.all_fields),
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
            await stream.get_final_response()  # Ensure stream is consumed
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
        
        for field_name in self.all_fields:
            field_obj = getattr(partial, field_name, None)
            
            if field_obj is None:
                state = FieldState(name=field_name, value=None, status=FieldStatus.NONE, timestamp=current_time)
            else:
                state = FieldState(name=field_name, value=field_obj, status=FieldStatus.COMPLETE, timestamp=current_time)
            
            field_states[field_name] = state
        
        return field_states
    
    def _display_partial_update(self, partial_count: int, elapsed: float, field_states: Dict[str, FieldState]):
        """Display the current state of all fields"""
        print(self.formatter.format_partial_header(partial_count, elapsed))
        
        for field_name in self.all_fields:
            field_state = field_states[field_name]
            is_required = field_name in self.required_fields
            display_name = self.introspector.get_field_display_name(self.model_class, field_name)
            line = self.formatter.format_field_line(field_state, display_name, is_required)
            print(line)
    
    @classmethod
    def create_dynamic_model(
        cls,
        fields: Dict[str, Any],
        required_fields: List[str],
        model_name: str = "DynamicModel"
    ) -> Type[BaseModel]:
        """Create a dynamic Pydantic model for simple use cases"""
        model_fields = {}
        
        for field_name in fields:
            json_schema_extra = {}
            if field_name in required_fields:
                json_schema_extra['required_for_execution'] = True
            
            model_fields[field_name] = Field(..., json_schema_extra=json_schema_extra)
        
        return type(model_name, (BaseModel,), {'__annotations__': fields, **model_fields})