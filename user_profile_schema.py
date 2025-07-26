#!/usr/bin/env python3
"""
UserProfile Pydantic Schema
============================

Defines the UserProfile schema with required field markers for BAML streaming.
This serves as both the data model AND the configuration for streaming behavior.
"""

from pydantic import BaseModel, Field
from typing import Optional


class UserProfile(BaseModel):
    """User profile schema with execution requirements embedded"""
    
    # Required fields for fast execution (marked with baml_required=True)
    name: str = Field(
        ..., 
        description="User's full name",
        json_schema_extra={"baml_required": True}
    )
    
    email: str = Field(
        ..., 
        description="User's email address",
        json_schema_extra={"baml_required": True}
    )
    
    is_verified: bool = Field(
        ..., 
        description="Account verification status",
        json_schema_extra={"baml_required": True}
    )
    
    # Optional fields (can complete after fast execution)
    bio: Optional[str] = Field(
        default=None, 
        description="User biography"
    )
    
    age: Optional[int] = Field(
        default=None, 
        description="User's age"
    )
    
    is_premium: Optional[bool] = Field(
        default=None, 
        description="Premium account status"
    )


# Example usage:
if __name__ == "__main__":
    from baml_streaming import get_required_fields, get_all_fields
    
    print("All fields:", get_all_fields(UserProfile))
    print("Required fields:", get_required_fields(UserProfile))
    
    for field_name in get_all_fields(UserProfile):
        field_info = UserProfile.model_fields.get(field_name)
        display_name = field_info.description if field_info and field_info.description else field_name
        required = field_name in get_required_fields(UserProfile)
        marker = "⭐" if required else "  "
        print(f"{marker} {field_name}: {display_name}")