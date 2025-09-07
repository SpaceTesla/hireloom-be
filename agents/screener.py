from schema import GraphState, CandidateProfile
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

def screener_node(state: GraphState):
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    ).with_structured_output(CandidateProfile)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """\
You are a helpful assistant that extracts structured information from a candidate's resume. 
Return the information in the exact format specified by the CandidateProfile schema.

IMPORTANT FORMATTING RULES:
- Use only standard ASCII characters and basic punctuation (no Unicode escape sequences)
- Use regular dashes (-) instead of em dashes (—) or en dashes (–)
- Use regular quotes (") instead of curly quotes ("")
- Use regular apostrophes (') instead of curly apostrophes ('')
- Phone numbers must be in E.164 format with + prefix (e.g., '+919876543210')
- If country code is missing, add '+91' for Indian numbers
- LinkedIn URLs should start with 'linkedin.com/in/'
- GitHub URLs should start with 'github.com/'
- When calculating years of experience, consider months as well. Every 3 months should be counted as 0.25 years of experience (e.g., 6 months = 0.5 years, 9 months = 0.75 years).

If the resume is not provided, return None.
If the resume is not in English, return None.
If the resume is not in a valid format, return None.
"""),
        ("human", """Analyze this resume and extract the following information:

Resume: {raw_resume_text}

Please extract:
- Personal info: name, email, phone, linkedin, github
- Education: level, university, graduation year
- Skills: programming languages, frontend, backend, database, devops
- Experience: total years, current role/company
- Projects: count and key project descriptions
- Achievements: hackathon wins, notable achievements
- Assessment: technical strength, experience level, fit score (1-10), key strengths, areas for improvement

For missing information, use appropriate defaults (empty lists, null values, etc.).
""")
    ])

    result = llm.invoke(prompt.invoke({"raw_resume_text": state.get("raw_resume_text", "No resume provided")}))
    state["candidate_profile"] = result  # Fixed the assignment

    return state
