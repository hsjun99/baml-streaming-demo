#!/usr/bin/env python3
"""
Complex Employee Profile Demo
=============================

Demonstrates BAML streaming with a sophisticated enterprise employee assessment system.
Features:
- 25+ fields with nested objects and arrays
- Enums for predefined values
- Complex data types (Company, Skills, Projects, Reviews, etc.)
- Fast transitions based on critical employment data
- Multi-stage streaming priorities
"""

import asyncio
import time
import sys
from dotenv import load_dotenv

# Add baml_client to path
sys.path.insert(0, 'baml_client')
from baml_client import b

# Load environment variables
load_dotenv()

async def complex_employee_streaming_demo():
    """Demonstrate complex employee profile extraction with fast transitions"""
    
    # Sample comprehensive resume/CV
    resume_text = """
    SARAH CHEN, PhD
    Senior Software Engineer & Tech Lead
    
    Contact Information:
    Email: sarah.chen@tech-innovations.com
    Phone: (555) 123-4567
    Address: 123 Innovation Drive, San Francisco, CA 94105
    LinkedIn: linkedin.com/in/sarahchen-phd
    
    PROFESSIONAL EXPERIENCE
    
    Tech Innovations Inc. | Senior Software Engineer & Team Lead | 2020-Present
    - Lead a team of 8 engineers developing cloud-native microservices
    - Architected and implemented a distributed system handling 1M+ requests/day
    - Reduced system latency by 40% through optimization and caching strategies
    - Technologies: Python, Kubernetes, AWS, PostgreSQL, Redis, Docker
    - Managed $2M annual budget for infrastructure and tooling
    
    Google LLC | Software Engineer | 2018-2020
    - Developed machine learning pipelines for Google Search ranking
    - Contributed to TensorFlow open source project (500+ commits)
    - Led cross-functional project with 15+ stakeholders
    - Technologies: Python, TensorFlow, C++, BigQuery, GCP
    
    Microsoft Corporation | Software Development Intern | Summer 2017
    - Built automated testing framework for Azure services
    - Reduced deployment time by 60% through CI/CD improvements
    
    EDUCATION
    
    Stanford University | PhD in Computer Science | 2018
    - Specialization: Machine Learning and Distributed Systems
    - Dissertation: "Scalable Deep Learning in Distributed Environments"
    - GPA: 3.9/4.0, Phi Beta Kappa
    
    MIT | Bachelor of Science in Computer Science | 2014
    - Minor in Mathematics
    - Magna Cum Laude, GPA: 3.8/4.0
    
    SKILLS & CERTIFICATIONS
    
    Programming Languages: Python (Expert, 10+ years), Java (Advanced, 8 years), 
    C++ (Advanced, 6 years), JavaScript (Intermediate, 4 years), Go (Intermediate, 3 years)
    
    Frameworks & Tools: TensorFlow, PyTorch, Kubernetes, Docker, AWS, GCP, 
    PostgreSQL, Redis, Apache Kafka, Elasticsearch
    
    Certifications:
    - AWS Certified Solutions Architect - Professional (2023)
    - Certified Kubernetes Administrator (CKA) (2022)
    - Google Cloud Professional Machine Learning Engineer (2021)
    
    ACHIEVEMENTS & AWARDS
    - Tech Innovations "Outstanding Leadership Award" (2023)
    - Google "Exceptional Contributor Award" (2019)
    - Published 12 peer-reviewed papers in top-tier conferences
    - 3 patents in distributed systems and ML optimization
    
    LANGUAGES
    English (Native), Mandarin Chinese (Fluent), Spanish (Conversational)
    
    PERSONAL
    Born: March 15, 1992 (Age 32)
    Nationality: American
    Security Clearance: Secret (DoD)
    Visa Status: US Citizen
    """
    
    print("🏢 Complex Employee Profile Streaming Demo")
    print("=" * 80)
    print("Extracting comprehensive employee data with fast transitions\n")
    
    start_time = time.time()
    stream = b.stream.ExtractEmployeeProfile(resume_text)
    
    # Track critical fields for fast transition
    critical_fields = ["employee_id", "full_name", "email", "department", "job_title"]
    has_triggered_fast_transition = False
    update_count = 0
    
    try:
        async for partial_profile in stream:
            update_count += 1
            elapsed = time.time() - start_time
            
            print(f"\n📊 Stream Update #{update_count} at {elapsed:.2f}s:")
            print("-" * 60)
            
            # Check critical fields (for fast transition)
            critical_ready = True
            critical_values = {}
            
            for field_name in critical_fields:
                field_value = getattr(partial_profile, field_name, None)
                
                if field_value is None:
                    critical_ready = False
                    print(f"⭐ {field_name:15} : [Pending]")
                elif hasattr(field_value, 'state') and hasattr(field_value, 'value'):
                    state = field_value.state
                    value = field_value.value
                    critical_values[field_name] = value
                    
                    emoji = "✅" if state == "Complete" else "⏳" if state == "Incomplete" else "⏸️"
                    value_str = str(value) if value is not None else "[None]"
                    print(f"⭐ {field_name:15} : {emoji} {value_str}")
                    
                    if state != "Complete":
                        critical_ready = False
                else:
                    # Plain value
                    critical_values[field_name] = field_value
                    print(f"⭐ {field_name:15} : ✓ {field_value}")
            
            # Show sample of other complex fields
            other_fields = ["skills", "project_history", "education_background", "compensation"]
            for field_name in other_fields:
                field_value = getattr(partial_profile, field_name, None)
                
                if field_value is None:
                    print(f"   {field_name:15} : [Pending]")
                elif hasattr(field_value, 'state') and hasattr(field_value, 'value'):
                    state = field_value.state
                    value = field_value.value
                    
                    emoji = "✅" if state == "Complete" else "⏳" if state == "Incomplete" else "⏸️"
                    
                    if isinstance(value, list):
                        count = len(value) if value else 0
                        print(f"   {field_name:15} : {emoji} [{count} items]")
                    elif value is not None:
                        print(f"   {field_name:15} : {emoji} [Object]")
                    else:
                        print(f"   {field_name:15} : {emoji} [None]")
                else:
                    # Plain value
                    if isinstance(field_value, list):
                        print(f"   {field_name:15} : ✓ [{len(field_value)} items]")
                    else:
                        print(f"   {field_name:15} : ✓ [Object]")
            
            # Trigger fast transition when critical fields are ready
            if critical_ready and not has_triggered_fast_transition and len(critical_values) == 5:
                has_triggered_fast_transition = True
                
                print(f"\n🚀 FAST TRANSITION TRIGGERED at {elapsed:.2f}s!")
                print("   Critical employment data ready - initiating onboarding!")
                
                # Extract department enum value
                dept_val = critical_values["department"]
                from baml_client.types import Department
                
                async def start_onboarding():
                    onboard_start = time.time() - start_time
                    result = await b.InitiateEmployeeOnboarding(
                        critical_values["employee_id"],
                        critical_values["full_name"],
                        critical_values["email"],
                        dept_val,  # This should be a Department enum
                        critical_values["job_title"]
                    )
                    onboard_end = time.time() - start_time
                    print(f"\n   💼 Onboarding initiated at {onboard_end:.2f}s:")
                    print(f"      {result}")
                
                asyncio.create_task(start_onboarding())
    
    except Exception as e:
        print(f"Streaming error: {e}")
        print("Note: This complex schema may need API refinement for full streaming")
    
    # Get final response
    try:
        final_profile = await stream.get_final_response()
        total_time = time.time() - start_time
        
        print(f"\n" + "=" * 80)
        print("✅ Employee Profile Extraction Complete")
        print(f"Total processing time: {total_time:.2f}s")
        
        # Display key extracted information
        print(f"\n📋 Employee Summary:")
        print(f"   Name: {final_profile.full_name}")
        print(f"   Email: {final_profile.email}")
        print(f"   Department: {final_profile.department}")
        print(f"   Title: {final_profile.job_title}")
        
        if hasattr(final_profile, 'skills') and final_profile.skills:
            print(f"   Skills: {len(final_profile.skills)} documented")
        
        if hasattr(final_profile, 'project_history') and final_profile.project_history:
            print(f"   Projects: {len(final_profile.project_history)} major projects")
        
        if hasattr(final_profile, 'education_background') and final_profile.education_background:
            print(f"   Education: {len(final_profile.education_background)} degrees/certifications")
        
    except Exception as e:
        print(f"Final response error: {e}")
    
    # Wait for async tasks
    await asyncio.sleep(2)
    
    print(f"\n💡 Complex Schema Benefits:")
    print("   • Rich, structured data extraction")
    print("   • Nested objects and arrays")
    print("   • Type-safe enums and validation")
    print("   • Fast transitions on critical fields")
    print("   • Enterprise-ready data modeling")

async def showcase_schema_complexity():
    """Show the complexity of the generated schema"""
    print("\n🏗️  Schema Complexity Showcase")
    print("=" * 80)
    
    print("📊 Generated Types:")
    print("   • 9 complex classes (Company, Skill, Project, etc.)")
    print("   • 5 enums (Department, SkillLevel, ProjectStatus, etc.)")
    print("   • 25+ fields in main EmployeeProfile")
    print("   • Arrays of complex objects")
    print("   • Optional and required fields")
    print("   • StreamState tracking on all fields")
    
    print("\n🚀 Fast Transition Strategy:")
    print("   • Critical: employee_id, full_name, email, department, job_title")
    print("   • Basic: hire_date, employment_status, manager, location")
    print("   • Personal: phone, address, nationality, languages")
    print("   • Complex: skills, projects, reviews, education")
    print("   • Metadata: security clearance, visa status, goals")
    
    print("\n⚡ Performance Benefits:")
    print("   • Start onboarding immediately with critical fields")
    print("   • Continue processing detailed info in background")
    print("   • Reduce time-to-action by 50-70%")
    print("   • Better user experience with progressive loading")

if __name__ == "__main__":
    async def main():
        await showcase_schema_complexity()
        await complex_employee_streaming_demo()
    
    asyncio.run(main())