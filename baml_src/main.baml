generator PythonClient {
  output_type "python/pydantic"
  output_dir "../baml_client"
  version "0.202.1"
  default_client_mode "async"
}

// Simple User Profile for streaming demo
class UserProfile {
  // Critical fields needed for next job execution (3 required)
  name string @stream.not_null @stream.done
  email string @stream.not_null @stream.done
  is_verified bool @stream.done
  
  // Optional fields that can stream with state information
  bio string
  age int
  is_premium bool
}

// Define the client
client<llm> GPT4o {
  provider openai
  options {
    model gpt-4.1-mini
    api_key env.OPENAI_API_KEY
    supports_streaming true
  }
}

// Function to extract user profile from text
function ExtractUserProfile(user_text: string) -> UserProfile {
  client GPT4o
  prompt #"
    You are a professional data extraction expert. Analyze the following text and extract user profile information.

    Text to analyze:
    {{ user_text }}
    
    Extract the following information:
    
    1. name: Extract the person's full name
    2. email: Find and extract their email address
    3. is_verified: Determine if this person appears to be verified/credible (true/false)
    4. bio: Create a biographical description (2-3 sentences)
    5. age: Extract their age if mentioned, or make a reasonable inference
    6. is_premium: Determine if this person qualifies for premium status (true/false)
    
    {{ ctx.output_format }}
  "#
}

// Function that represents the "next job" - only needs name and email
function ProcessUser(name: string, email: string) -> string {
  client GPT4o
  prompt #"
    Generate a welcome message for:
    Name: {{ name }}
    Email: {{ email }}
    
    Create a personalized welcome message.
  "#
}