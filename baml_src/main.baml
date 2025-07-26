generator PythonClient {
  output_type "python/pydantic"
  output_dir "../baml_client"
  version "0.202.1"
  default_client_mode "async"
}

// Enterprise Employee Assessment System - Complex Schema
// =======================================================

// Enums for predefined values
enum Department {
  ENGINEERING
  MARKETING  
  SALES
  HR
  FINANCE
  OPERATIONS
  LEGAL
  DESIGN
  PRODUCT
}

enum SkillLevel {
  BEGINNER
  INTERMEDIATE  
  ADVANCED
  EXPERT
}

enum ProjectStatus {
  PLANNING
  IN_PROGRESS
  COMPLETED
  ON_HOLD
  CANCELLED
}

enum ReviewRating {
  EXCEEDS_EXPECTATIONS
  MEETS_EXPECTATIONS
  BELOW_EXPECTATIONS
  NEEDS_IMPROVEMENT
}

enum EducationLevel {
  HIGH_SCHOOL
  ASSOCIATES
  BACHELORS
  MASTERS
  PHD
  CERTIFICATE
}

// Nested complex classes
class Company {
  name string
  industry string
  size_employees int
  headquarters_location string
  stock_symbol string?
}

class Skill {
  name string
  category string
  level SkillLevel
  years_experience int
  last_used_year int?
  certified bool
}

class Certification {
  name string
  issuing_organization string
  issue_date string
  expiry_date string?
  credential_id string?
  is_active bool
}

class Project {
  name string
  description string
  status ProjectStatus
  start_date string
  end_date string?
  budget_usd float?
  team_size int
  role_in_project string
  technologies_used string[]
  key_achievements string[]
}

class PerformanceReview {
  review_period string
  overall_rating ReviewRating
  goals_met_percentage float
  strengths string[]
  areas_for_improvement string[]
  manager_feedback string
  career_development_plan string?
  salary_change_percentage float?
}

class Education {
  institution string
  degree string
  field_of_study string
  level EducationLevel
  graduation_year int
  gpa float?
  honors string?
}

class EmergencyContact {
  name string
  relationship string
  phone string
  email string?
  address string?
}

class CompensationDetails {
  base_salary_usd float
  bonus_percentage float?
  equity_shares int?
  benefits_value_usd float?
  total_compensation_usd float
}

// Main complex entity
class EmployeeProfile {
  // Critical fields for immediate processing (fast transition triggers)
  employee_id string @stream.with_state @stream.not_null
  full_name string @stream.with_state @stream.not_null  
  email string @stream.with_state @stream.not_null
  department Department @stream.with_state @stream.not_null
  job_title string @stream.with_state @stream.not_null
  
  // Basic employment info (somewhat critical)
  hire_date string @stream.with_state
  employment_status string @stream.with_state  // "active", "contractor", "intern"
  manager_name string @stream.with_state
  office_location string @stream.with_state
  is_remote bool @stream.with_state
  
  // Personal details (can stream later)
  phone string @stream.with_state
  date_of_birth string @stream.with_state
  address string @stream.with_state
  nationality string @stream.with_state
  languages_spoken string[] @stream.with_state
  
  // Complex nested objects (stream after basic info)
  company Company @stream.with_state
  skills Skill[] @stream.with_state
  certifications Certification[] @stream.with_state
  project_history Project[] @stream.with_state
  performance_reviews PerformanceReview[] @stream.with_state
  education_background Education[] @stream.with_state
  emergency_contacts EmergencyContact[] @stream.with_state
  compensation CompensationDetails @stream.with_state
  
  // Additional metadata (least critical, stream last)
  security_clearance_level string? @stream.with_state
  visa_status string? @stream.with_state
  professional_summary string @stream.with_state
  career_goals string @stream.with_state
  years_total_experience int @stream.with_state
  previous_companies string[] @stream.with_state
  
  // Computed/derived fields
  is_senior_level bool @stream.with_state
  performance_score float @stream.with_state
  skill_diversity_score float @stream.with_state
  promotion_eligible bool @stream.with_state
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

// Function to extract comprehensive employee profile from resume/CV text
function ExtractEmployeeProfile(resume_text: string) -> EmployeeProfile {
  client GPT4o
  prompt #"
    You are an expert HR data extraction specialist. Analyze the following resume/CV text and extract comprehensive employee profile information. Be thorough and detailed, inferring reasonable values where appropriate.

    Resume/CV Text:
    {{ resume_text }}
    
    Extract and structure the following information:
    
    CRITICAL INFORMATION (extract first):
    - employee_id: Generate a reasonable ID like "EMP" + random number
    - full_name: Complete name with titles if present
    - email: Professional email address
    - department: Choose from ENGINEERING, MARKETING, SALES, HR, FINANCE, OPERATIONS, LEGAL, DESIGN, PRODUCT
    - job_title: Current or most recent position
    
    EMPLOYMENT DETAILS:
    - hire_date, employment_status, manager_name, office_location, is_remote
    
    PERSONAL INFORMATION:
    - phone, date_of_birth, address, nationality, languages_spoken
    
    COMPLEX NESTED DATA:
    - company: Extract company details with name, industry, size, location
    - skills: List with categories, proficiency levels (BEGINNER/INTERMEDIATE/ADVANCED/EXPERT), years of experience
    - certifications: Professional certifications with dates and issuing organizations
    - project_history: Major projects with descriptions, status, dates, technologies, achievements
    - performance_reviews: Infer from achievements and career progression
    - education_background: Schools, degrees, graduation years, GPAs if mentioned
    - emergency_contacts: If mentioned, otherwise create reasonable placeholder
    - compensation: Estimate based on role and experience level
    
    DERIVED METRICS:
    - years_total_experience: Calculate from career timeline
    - is_senior_level: Based on experience and role
    - performance_score: Estimate 1-5 based on achievements
    - skill_diversity_score: Rate 1-5 based on breadth of skills
    - promotion_eligible: Based on performance and tenure
    
    Be comprehensive and realistic. Where information isn't explicit, make reasonable professional inferences based on the context provided.
    
    {{ ctx.output_format }}
  "#
}

// Fast transition function - triggers when critical fields are ready
function InitiateEmployeeOnboarding(
  employee_id: string, 
  full_name: string, 
  email: string, 
  department: Department, 
  job_title: string
) -> string {
  client GPT4o
  prompt #"
    Generate an employee onboarding initiation message for:
    
    Employee ID: {{ employee_id }}
    Name: {{ full_name }}
    Email: {{ email }}
    Department: {{ department }}
    Title: {{ job_title }}
    
    Create a professional onboarding welcome message that:
    1. Welcomes them to the company
    2. Mentions their department and role
    3. Outlines next steps in the onboarding process
    4. Provides their employee ID for reference
    
    Keep it professional but warm, and mention that additional profile information is being processed.
  "#
}

// Function to analyze complex employee data for insights
function AnalyzeEmployeeProfile(profile: EmployeeProfile) -> string {
  client GPT4o
  prompt #"
    Analyze this comprehensive employee profile and provide insights:
    
    {{ profile }}
    
    Provide a detailed analysis covering:
    1. Overall profile strength and experience level
    2. Key skills and competencies
    3. Career progression and achievements
    4. Potential areas for development
    5. Recommended role assignments or projects
    6. Performance indicators and trends
    
    Focus on actionable insights for HR and management decisions.
  "#
}