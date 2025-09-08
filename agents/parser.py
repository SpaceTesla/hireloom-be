from langchain_pymupdf4llm import PyMuPDF4LLMLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from schema import GraphState, CandidateProfile
from dotenv import load_dotenv
import os
import json

load_dotenv()

def parser_node(state: GraphState):
    """
    Unified parser node that:
    1. Extracts text from PDF
    2. Parses it into structured JSON format
    3. Saves the parsed data
    """
    # Step 1: Extract text from PDF
    loader = PyMuPDF4LLMLoader(file_path=state["resume_path"])
    docs = [doc for doc in loader.lazy_load()]
    content = "\n\n".join([doc.page_content for doc in docs])
    state["raw_resume_text"] = content
    
    # Step 2: Parse into structured data using LLM
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
- Basic assessment: technical strength, experience level

For missing information, use appropriate defaults (empty lists, null values, etc.).
""")
    ])

    # Parse the resume into structured data
    result = llm.invoke(prompt.invoke({"raw_resume_text": content}))
    state["candidate_profile"] = result
    
    # Step 3: Save parsed data to JSON file
    if result:
        # Extract filename from resume_path for naming the output file
        resume_filename = os.path.basename(state["resume_path"])
        candidate_name = result.name.lower().replace(" ", "_")
        output_filename = f"{candidate_name}.json"
        output_path = os.path.join("storage", "results", output_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
        
        print(f"✅ Parsed resume saved to: {output_path}")
    
    return state
