#!/usr/bin/env python3
"""
Add sample data for testing pagination
"""

import requests
import json

def add_sample_data():
    """Add sample data to test pagination"""
    base_url = "http://localhost:8000/api/v1"
    
    sample_data = [
        {
            "title": "John Smith - Software Engineer",
            "description": "Experienced full-stack developer with expertise in React and Node.js",
            "content": {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "age": 29,
                "city": "San Francisco",
                "occupation": "Software Engineer",
                "skills": ["JavaScript", "React", "Node.js", "MongoDB"],
                "experience": 5
            },
            "tags": ["software", "engineer", "fullstack", "react"],
            "category": "Job"
        },
        {
            "title": "Sarah Johnson - Data Scientist",
            "description": "Data scientist with strong background in machine learning and analytics",
            "content": {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@email.com",
                "age": 31,
                "city": "New York",
                "occupation": "Data Scientist",
                "skills": ["Python", "Machine Learning", "SQL", "Pandas"],
                "experience": 7
            },
            "tags": ["data science", "ML", "python", "analytics"],
            "category": "Job"
        },
        {
            "title": "Mike Chen - Product Manager",
            "description": "Product manager with experience in agile development and user research",
            "content": {
                "name": "Mike Chen",
                "email": "mike.chen@email.com",
                "age": 33,
                "city": "Seattle",
                "occupation": "Product Manager",
                "skills": ["Product Strategy", "Agile", "User Research", "Analytics"],
                "experience": 8
            },
            "tags": ["product", "management", "agile", "strategy"],
            "category": "Job"
        },
        {
            "title": "Emily Davis - UX Designer",
            "description": "Creative UX designer focused on user-centered design principles",
            "content": {
                "name": "Emily Davis",
                "email": "emily.davis@email.com",
                "age": 27,
                "city": "Austin",
                "occupation": "UX Designer",
                "skills": ["Figma", "User Research", "Prototyping", "Design Systems"],
                "experience": 4
            },
            "tags": ["design", "UX", "UI", "prototyping"],
            "category": "Job"
        },
        {
            "title": "Alex Rodriguez - DevOps Engineer",
            "description": "DevOps engineer specializing in cloud infrastructure and automation",
            "content": {
                "name": "Alex Rodriguez",
                "email": "alex.rodriguez@email.com",
                "age": 30,
                "city": "Denver",
                "occupation": "DevOps Engineer",
                "skills": ["AWS", "Docker", "Kubernetes", "Terraform"],
                "experience": 6
            },
            "tags": ["devops", "cloud", "aws", "automation"],
            "category": "Job"
        },
        {
            "title": "Lisa Wang - Marketing Specialist",
            "description": "Digital marketing specialist with focus on content and social media",
            "content": {
                "name": "Lisa Wang",
                "email": "lisa.wang@email.com",
                "age": 28,
                "city": "Los Angeles",
                "occupation": "Marketing Specialist",
                "skills": ["Content Marketing", "Social Media", "SEO", "Analytics"],
                "experience": 5
            },
            "tags": ["marketing", "digital", "content", "social media"],
            "category": "Marketing"
        },
        {
            "title": "David Brown - Sales Manager",
            "description": "Experienced sales manager with track record in B2B software sales",
            "content": {
                "name": "David Brown",
                "email": "david.brown@email.com",
                "age": 35,
                "city": "Chicago",
                "occupation": "Sales Manager",
                "skills": ["B2B Sales", "CRM", "Team Leadership", "Customer Relations"],
                "experience": 10
            },
            "tags": ["sales", "B2B", "management", "CRM"],
            "category": "Sales"
        },
        {
            "title": "Jennifer Taylor - HR Specialist",
            "description": "HR specialist focused on talent acquisition and employee development",
            "content": {
                "name": "Jennifer Taylor",
                "email": "jennifer.taylor@email.com",
                "age": 32,
                "city": "Boston",
                "occupation": "HR Specialist",
                "skills": ["Recruitment", "Employee Relations", "Performance Management", "Training"],
                "experience": 7
            },
            "tags": ["HR", "recruitment", "training", "management"],
            "category": "HR"
        },
        {
            "title": "Robert Kim - Business Analyst",
            "description": "Business analyst with expertise in process optimization and data analysis",
            "content": {
                "name": "Robert Kim",
                "email": "robert.kim@email.com",
                "age": 29,
                "city": "Miami",
                "occupation": "Business Analyst",
                "skills": ["Business Analysis", "Process Improvement", "SQL", "Excel"],
                "experience": 5
            },
            "tags": ["business", "analyst", "process", "data"],
            "category": "Business"
        },
        {
            "title": "Amanda Wilson - Graphic Designer",
            "description": "Creative graphic designer with experience in branding and digital design",
            "content": {
                "name": "Amanda Wilson",
                "email": "amanda.wilson@email.com",
                "age": 26,
                "city": "Portland",
                "occupation": "Graphic Designer",
                "skills": ["Adobe Creative Suite", "Branding", "Print Design", "Web Design"],
                "experience": 4
            },
            "tags": ["design", "graphic", "branding", "creative"],
            "category": "Design"
        },
        {
            "title": "Kevin Lee - QA Engineer",
            "description": "Quality assurance engineer with expertise in automated testing",
            "content": {
                "name": "Kevin Lee",
                "email": "kevin.lee@email.com",
                "age": 27,
                "city": "San Diego",
                "occupation": "QA Engineer",
                "skills": ["Test Automation", "Selenium", "API Testing", "Bug Tracking"],
                "experience": 4
            },
            "tags": ["QA", "testing", "automation", "selenium"],
            "category": "Job"
        },
        {
            "title": "Rachel Green - Content Writer",
            "description": "Professional content writer specializing in technical documentation",
            "content": {
                "name": "Rachel Green",
                "email": "rachel.green@email.com",
                "age": 25,
                "city": "Nashville",
                "occupation": "Content Writer",
                "skills": ["Technical Writing", "Content Strategy", "SEO Writing", "Research"],
                "experience": 3
            },
            "tags": ["writing", "content", "technical", "documentation"],
            "category": "Content"
        }
    ]
    
    print("Adding sample data for pagination testing...")
    print("=" * 50)
    
    created_records = []
    for i, record in enumerate(sample_data, 1):
        try:
            response = requests.post(
                f"{base_url}/data/",
                json=record,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                created = response.json()
                created_records.append(created["id"])
                print(f"✅ {i:2d}. Created: {record['title']}")
            else:
                print(f"❌ {i:2d}. Failed: {record['title']} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {i:2d}. Error: {record['title']} - {e}")
    
    print(f"\n✅ Successfully created {len(created_records)} sample records")
    print("\nNow you can test pagination in your frontend!")
    print("- Each page will show 10 records")
    print("- Use the pagination controls to navigate between pages")
    print("- Total records should be:", len(created_records) + 1)  # +1 for existing Naman record
    
    return created_records

if __name__ == "__main__":
    try:
        add_sample_data()
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
    except Exception as e:
        print(f"Error: {e}")