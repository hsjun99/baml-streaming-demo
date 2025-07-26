generator PythonClient {
  output_type "python/pydantic"
  output_dir "../baml_client"
  version "0.202.1"
  default_client_mode "async"
}

// Define an entity with 4 fields
class UserProfile {
  // Critical fields needed for next job execution (only 2 required)
  // These use @stream.done so they only appear when complete
  name string @stream.done @stream.not_null
  email string @stream.done @stream.not_null
  
  // Optional fields that can stream with state information
  bio string @stream.with_state
  age int @stream.with_state
}

// Define the client
client<llm> GPT4oMini {
  provider openai
  options {
    model gpt-4o-mini
    api_key env.OPENAI_API_KEY
    supports_streaming true
  }
}

// Function to extract user profile from text
function ExtractUserProfile(user_text: string) -> UserProfile {
  client GPT4oMini
  prompt #"
    You are a professional data extraction expert. Please carefully analyze the following text and extract detailed user profile information. Take your time to provide a comprehensive response with rich details for each field.

    Text to analyze:
    {{ user_text }}
    
    Please extract the following information with detailed explanations:
    
    1. name: Extract the person's full name. If middle names or titles are present, include them.
    
    2. email: Find and extract their email address. Verify it follows standard email format.
    
    3. bio: Create a comprehensive biographical description. Include their profession, experience, interests, background, skills, and any other relevant personal or professional details mentioned. Make this detailed and informative - aim for at least 2-3 sentences that capture their essence and background.
    
    4. age: Extract their age if explicitly mentioned, or make a reasonable inference based on career experience and other contextual clues.
    
    Please provide detailed, well-reasoned responses for each field. Think step by step and be thorough in your analysis.
    
    {{ ctx.output_format }}
  "#
}

// Function that represents the "next job" - only needs name and email
function ProcessUser(name: string, email: string) -> string {
  client GPT4oMini
  prompt #"
    Generate a welcome message for:
    Name: {{ name }}
    Email: {{ email }}
    
    Create a personalized welcome message.
  "#
}