from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from schema import GraphState, ScreeningResult
from dotenv import load_dotenv
import os
import json

load_dotenv()

def screener_agent(state: GraphState):
    """
    Screener agent that compares candidate profile against job description
    and provides comprehensive screening analysis with scores and recommendations.
    """
    candidate_profile = state.get("candidate_profile")
    job_description = state.get("job_description")
    
    if not candidate_profile:
        raise ValueError("No candidate profile found in state")
    
    if not job_description:
        raise ValueError("No job description found in state")
    
    # Initialize LLM with structured output
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(ScreeningResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """\
You are an expert technical recruiter and hiring manager with 10+ years of experience. 
Your task is to thoroughly analyze a candidate's profile against a job description and provide 
comprehensive screening insights.

ANALYSIS FRAMEWORK:
1. Technical Skills Match (40% weight)
2. Experience Level Match (30% weight) 
3. Cultural/Soft Skills Fit (20% weight)
4. Overall Potential (10% weight)

SCORING GUIDELINES:
- 9-10: Exceptional match, exceeds requirements
- 7-8: Strong match, meets most requirements
- 5-6: Moderate match, some gaps but potential
- 3-4: Weak match, significant gaps
- 1-2: Poor match, major concerns

HIRING RECOMMENDATIONS:
- Strong Hire: 8+ overall score, clear strengths, minimal concerns
- Hire: 6-7 overall score, good fit with some development areas
- Maybe: 4-5 overall score, potential but significant gaps
- Pass: 1-3 overall score, major misalignment

Be thorough, objective, and provide actionable insights for hiring decisions.
"""),
        ("human", """\
Analyze this candidate against the job description:

CANDIDATE PROFILE:
Name: {candidate_name}
Email: {candidate_email}
Phone: {candidate_phone}
LinkedIn: {candidate_linkedin}
GitHub: {candidate_github}

Education: {education_level} from {university} ({graduation_year})
Total Experience: {total_experience_years} years
Current Role: {current_role} at {current_company}

Technical Skills: {technical_skills}
Soft Skills: {soft_skills}
Other Skills: {other_skills}

Projects: {project_count} projects
Key Projects: {key_projects}

Achievements: {hackathon_wins} hackathon wins
Notable Achievements: {notable_achievements}

Technical Strength: {technical_strength}
Experience Level: {experience_level}

JOB DESCRIPTION:
{job_description}

Please provide a comprehensive screening analysis including:
1. Detailed scores for technical fit, experience fit, cultural fit, and overall fit
2. Key strengths and weaknesses specific to this role
3. Skills analysis (matching skills, gaps, missing skills)
4. Experience assessment and seniority level evaluation
5. Clear hiring recommendation with confidence level
6. Detailed reasoning for the recommendation
7. Interview focus areas and onboarding suggestions
8. Salary expectations based on the profile

Be specific and actionable in your analysis.
""")
    ])

    # Format candidate data for the prompt
    candidate_data = {
        "candidate_name": candidate_profile.name,
        "candidate_email": candidate_profile.email,
        "candidate_phone": candidate_profile.phone or "Not provided",
        "candidate_linkedin": candidate_profile.linkedin or "Not provided",
        "candidate_github": candidate_profile.github or "Not provided",
        "education_level": candidate_profile.education_level,
        "university": candidate_profile.university,
        "graduation_year": candidate_profile.graduation_year or "Not specified",
        "total_experience_years": candidate_profile.total_experience_years,
        "current_role": candidate_profile.current_role or "Not specified",
        "current_company": candidate_profile.current_company or "Not specified",
        "technical_skills": ", ".join(candidate_profile.technical_skills) if candidate_profile.technical_skills else "Not specified",
        "soft_skills": ", ".join(candidate_profile.soft_skills) if candidate_profile.soft_skills else "Not specified",
        "other_skills": ", ".join(candidate_profile.other_skills) if candidate_profile.other_skills else "Not specified",
        "project_count": candidate_profile.project_count,
        "key_projects": "; ".join(candidate_profile.key_projects) if candidate_profile.key_projects else "Not specified",
        "hackathon_wins": candidate_profile.hackathon_wins,
        "notable_achievements": "; ".join(candidate_profile.notable_achievements) if candidate_profile.notable_achievements else "Not specified",
        "technical_strength": candidate_profile.technical_strength,
        "experience_level": candidate_profile.experience_level,
        "job_description": job_description
    }

    # Get screening analysis
    result = llm.invoke(prompt.invoke(candidate_data))
    state["screening_result"] = result
    
    # Save screening result to JSON file
    if result:
        # Extract candidate name for filename
        candidate_name = candidate_profile.name.lower().replace(" ", "_")
        output_filename = f"{candidate_name}_screening.json"
        output_path = os.path.join("storage", "results", output_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Screening analysis saved to: {output_path}")
        print(f"📊 Overall Fit Score: {result.overall_fit_score}/10")
        print(f"🎯 Recommendation: {result.hiring_recommendation} ({result.confidence_level} confidence)")
    
    return state
