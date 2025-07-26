generator PythonClient {
  output_type "python/pydantic"
  output_dir "../baml_client"
  version "0.202.1"
  default_client_mode "async"
}

// Define an entity with 6 fields
class UserProfile {
  // Critical fields needed for next job execution (3 required)
  // These use @stream.with_state to track progress and completion state
  name string @stream.with_state @stream.not_null
  email string @stream.with_state @stream.not_null
  is_verified bool @stream.with_state @stream.not_null
  
  // Optional fields that can stream with state information
  bio string @stream.with_state
  age int @stream.with_state
  is_premium bool @stream.with_state
}

// Define the client
client<llm> GPT4o {
  provider openai
  options {
    model gpt-4o
    api_key env.OPENAI_API_KEY
    supports_streaming true
  }
}

// Function to extract user profile from text
function ExtractUserProfile(user_text: string) -> UserProfile {
  client GPT4o
  prompt #"
    You are a professional data extraction expert. Please carefully analyze the following text and extract detailed user profile information. Take your time to provide a comprehensive response with rich details for each field.

    Text to analyze:
    {{ user_text }}
    
    Please extract the following information with detailed explanations:
    
    1. name: Extract the person's full name. If middle names or titles are present, include them.
    
    2. email: Find and extract their email address. Verify it follows standard email format.
    
    3. is_verified: Determine if this person appears to be a verified/legitimate professional based on their credentials, affiliations, and background. Return true if they have clear professional credentials (PhD, university affiliation, published work, etc.), false otherwise.
    
    4. bio: Create a comprehensive biographical description. Include their profession, experience, interests, background, skills, and any other relevant personal or professional details mentioned. Make this detailed and informative - aim for at least 2-3 sentences that capture their essence and background.
    
    5. age: Extract their age if explicitly mentioned, or make a reasonable inference based on career experience and other contextual clues.
    
    6. is_premium: Determine if this person likely qualifies for premium status based on their professional level, experience, and achievements. Return true for senior professionals, executives, PhDs, or those with 10+ years experience, false for junior professionals.
    
    Please provide detailed, well-reasoned responses for each field. Think step by step and be thorough in your analysis.
    
    {{ ctx.output_format }}
  "#
}

// Function that represents the "next job" - only needs name, email, and verification status
function ProcessUser(name: string, email: string, is_verified: bool) -> string {
  client GPT4o
  prompt #"
    Generate a welcome message for:
    Name: {{ name }}
    Email: {{ email }}
    Verified Status: {{ is_verified }}
    
    Create a personalized welcome message that acknowledges their verification status.
    If verified, mention their professional credentials. If not verified, use a standard welcome.
  "#
}