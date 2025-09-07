from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field, field_validator, HttpUrl
import re


class CandidateProfile(BaseModel):
    """Structured candidate information extracted from resume"""
    name: str
    email: str = Field(description="Email address of the candidate")
    phone: Optional[str] = Field(default="", description="Phone number in E.164 format (e.g., '+919876543210'). Defaults to '+91' if country code is missing")
    linkedin: Optional[str] = Field(default="", description="LinkedIn profile URL of the candidate")
    github: Optional[str] = Field(default="", description="GitHub profile URL of the candidate")
    
    # Education
    education_level: str = Field(description="Education level: Bachelor's, Master's, High School, etc.")
    university: str = Field(description="University of the candidate")
    graduation_year: Optional[int] = Field(default=None, description="Graduation year of the candidate")
    
    # Skills
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    other_skills: List[str] = Field(default_factory=list)
    
    # Experience
    total_experience_years: float = Field(ge=0, description="Total years of experience")
    current_role: Optional[str] = Field(default=None, description="Current role of the candidate")
    current_company: Optional[str] = Field(default=None, description="Current company of the candidate")
    
    # Projects
    project_count: int = Field(ge=0, description="Number of projects")
    key_projects: List[str] = Field(default_factory=list, description="Brief descriptions of main projects")
    
    # Achievements
    hackathon_wins: int = Field(ge=0, description="Number of hackathon wins")
    notable_achievements: List[str] = Field(default_factory=list)
    
    # Overall assessment
    technical_strength: str = Field(description="Technical strength: Strong, Moderate, or Beginner")
    experience_level: str = Field(description="Experience level: Senior, Mid-level, or Junior")
    fit_score: int = Field(ge=1, le=10, description="Fit score from 1 to 10")
    key_strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not v:  # Allow empty string
            return v
        
        # Remove any spaces or dashes
        cleaned = re.sub(r'[\s\-]', '', v)
        
        # If it doesn't start with +, assume it's Indian number and add +91
        if not cleaned.startswith('+'):
            if cleaned.startswith('91') and len(cleaned) == 12:
                # Already has country code, just add +
                cleaned = '+' + cleaned
            elif len(cleaned) == 10:
                # 10 digit number, add +91
                cleaned = '+91' + cleaned
            else:
                # Try to add +91 for other cases
                cleaned = '+91' + cleaned
        
        # E.164 format: + followed by up to 15 digits
        phone_pattern = r'^\+\d{1,15}$'
        if not re.match(phone_pattern, cleaned):
            raise ValueError('Phone must be in E.164 format (e.g., +919876543210)')
        
        return cleaned
    
    @field_validator('linkedin')
    @classmethod
    def validate_linkedin(cls, v):
        if not v:  # Allow empty string
            return v
        if not v.startswith(('https://www.linkedin.com/', 'http://www.linkedin.com/', 'linkedin.com/')):
            raise ValueError('LinkedIn URL must be a valid LinkedIn profile URL')
        return v
    
    @field_validator('github')
    @classmethod
    def validate_github(cls, v):
        if not v:  # Allow empty string
            return v
        if not v.startswith(('https://github.com/', 'http://github.com/', 'github.com/')):
            raise ValueError('GitHub URL must be a valid GitHub profile URL')
        return v
    
    
    @field_validator('technical_strength')
    @classmethod
    def validate_technical_strength(cls, v):
        allowed_values = ["Strong", "Moderate", "Beginner"]
        if v not in allowed_values:
            raise ValueError(f"technical_strength must be one of {allowed_values}")
        return v
    
    @field_validator('experience_level')
    @classmethod
    def validate_experience_level(cls, v):
        allowed_values = ["Senior", "Mid-level", "Junior"]
        if v not in allowed_values:
            raise ValueError(f"experience_level must be one of {allowed_values}")
        return v


# Define the state for the graph
class GraphState(TypedDict):
    """State for the graph"""
    # messages: Annotated[list[BaseMessage], add_messages]
    candidate_profile: Optional[CandidateProfile]
    raw_resume_text: Optional[str]
    resume_path: Optional[str]
