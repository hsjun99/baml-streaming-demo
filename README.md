# BAML Streaming Demo: Fast Transitions

This demo showcases BAML's streaming capabilities with fast transitions - executing the next job as soon as the minimum required fields are available.

## Features

- **Streaming Entity Extraction**: Extracts user profile with 4 fields (name, email, bio, age)
- **Fast Transitions**: Triggers next job immediately when name + email are complete
- **State Management**: Uses useState-like pattern to track field completion
- **BAML Streaming Attributes**: Leverages `@stream.done` and `@stream.not_null`

## Project Structure

```
baml-streaming-test/
├── baml_src/           # BAML source files
│   ├── baml.toml      # BAML configuration
│   └── main.baml      # Function definitions
├── baml_client/       # Generated BAML client (auto-generated)
├── src/               # Python source code
│   └── streaming_demo.py
├── run_demo.py        # Main demo runner
├── pyproject.toml     # Poetry configuration
└── README.md
```

## Setup

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Set up environment**:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   # Or copy .env.example to .env and edit it
   ```

3. **Run the showcase demo** (no API key required):
   ```bash
   python demo_showcase.py
   ```

4. **Run the full demo** (requires API key):
   ```bash
   python run_demo.py
   ```

## How It Works

### 1. BAML Function Definition
The `UserProfile` class uses streaming attributes for comprehensive state tracking:
- `name` and `email` have `@stream.done @stream.not_null @stream.with_state` - complete when ready + state tracking
- `bio` has `@stream.with_state` - streams incrementally with state information
- `age` has `@stream.with_state` - appears when complete with state information

### 2. Fast Transitions
The demo monitors streaming responses and triggers the next job (`ProcessUser`) as soon as both `name` and `email` are available, without waiting for the full response.

### 3. State Management
Uses a `UserProfileState` class with:
- Field values as `StreamState[T]` objects containing value + completion state
- Completion status tracking for each field
- Callbacks for field updates and next job triggering
- useState-like pattern for consistent state management

## Expected Output

```
🎯 BAML Streaming Demo: Fast Transitions
============================================================
Scenario: Extract user profile and trigger next job as soon as name + email are available

Processing user input: Hi there! My name is Alice Johnson...
==================================================
🔄 Partial update received:
  ✅ Name complete: Alice Johnson

🔄 Partial update received:
  ✅ Email complete: alice.johnson@email.com

🚀 FAST TRANSITION: Required fields ready! Triggering next job...
   Name: Alice Johnson
   Email: alice.johnson@email.com

💬 Welcome message generated: Welcome Alice Johnson! We're excited to have you...

🔄 Partial update received:
  📝 Bio streaming: I'm a 28-year-old software engineer who loves...

🏁 Final response received:
  Name: Alice Johnson
  Email: alice.johnson@email.com
  Bio: I'm a 28-year-old software engineer who loves building AI applications...
  Age: 28
```

## Key Concepts

- **@stream.done**: Ensures fields only appear when completely finished
- **@stream.not_null**: Ensures containing object only streams when field has value  
- **@stream.with_state**: Provides `StreamState[T]` objects with value + completion state
- **Fast Transitions**: Execute dependent jobs as soon as minimum requirements are met
- **State Management**: Track field completion and trigger actions based on state changes
- **useState Pattern**: Consistent state management across all fields using StreamState