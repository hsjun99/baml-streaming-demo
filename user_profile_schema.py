#!/usr/bin/env python3
"""
UserProfile Pydantic Schema
============================

Defines the UserProfile schema with required field markers for BAML streaming.
This serves as both the data model AND the configuration for streaming behavior.
"""

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile schema with execution requirements embedded"""
    
    # Required fields for fast execution (marked with required_for_execution=True)
    name: str = Field(
        ..., 
        description="User's full name",
        json_schema_extra={"required_for_execution": True}
    )
    
    email: str = Field(
        ..., 
        description="User's email address",
        json_schema_extra={"required_for_execution": True}
    )
    
    is_verified: bool = Field(
        ..., 
        description="Account verification status",
        json_schema_extra={"required_for_execution": True}
    )
    
    # Optional fields (can complete after fast execution)
    bio: str = Field(
        ..., 
        description="User biography"
    )
    
    age: int = Field(
        ..., 
        description="User's age"
    )
    
    is_premium: bool = Field(
        ..., 
        description="Premium account status"
    )


# Example usage:
if __name__ == "__main__":
    from baml_streaming_helpers import SchemaIntrospector
    
    introspector = SchemaIntrospector()
    
    print("All fields:", introspector.get_all_field_names(UserProfile))
    print("Required fields:", introspector.get_required_fields(UserProfile))
    
    for field_name in introspector.get_all_field_names(UserProfile):
        display_name = introspector.get_field_display_name(UserProfile, field_name)
        required = field_name in introspector.get_required_fields(UserProfile)
        marker = "⭐" if required else "  "
        print(f"{marker} {field_name}: {display_name}")