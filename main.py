from core.build_graph import build_graph
import json


def main():
    app = build_graph()
    person_name = "shivansh"
    job_type = "frontend"  # or "devops"
    
    # Load job description
    with open(f"storage/jds/{job_type}.txt", "r", encoding="utf-8") as f:
        job_description = f.read()
    
    # Initial state
    initial_state = {
        "raw_resume_text": None,
        "resume_path": f"storage/resumes/{person_name}.pdf",
        "candidate_profile": None,
        "job_description": job_description,
        "screening_result": None
    }
    
    print(f"🔍 Processing {person_name}'s resume against {job_type} job description...")
    
    # Run the workflow
    result_state = app.invoke(initial_state)

    # Display results
    if result_state.get("candidate_profile"):
        print(f"\n✅ Candidate Profile Parsed: {result_state['candidate_profile'].name}")
    
    if result_state.get("screening_result"):
        screening = result_state["screening_result"]
        print(f"\n📊 SCREENING RESULTS:")
        print(f"Overall Fit Score: {screening.overall_fit_score}/10")
        print(f"Technical Fit: {screening.technical_fit_score}/10")
        print(f"Experience Fit: {screening.experience_fit_score}/10")
        print(f"Cultural Fit: {screening.cultural_fit_score}/10")
        print(f"\n🎯 RECOMMENDATION: {screening.hiring_recommendation}")
        print(f"Confidence: {screening.confidence_level}")
        print(f"\n💡 Reasoning: {screening.reasoning}")
        
        print(f"\n✅ Strengths:")
        for strength in screening.key_strengths:
            print(f"  • {strength}")
            
        print(f"\n⚠️  Weaknesses:")
        for weakness in screening.key_weaknesses:
            print(f"  • {weakness}")
            
        print(f"\n🎯 Interview Focus Areas:")
        for area in screening.interview_focus_areas:
            print(f"  • {area}")

    print(f"\n📁 Results saved to storage/results/")


if __name__ == "__main__":
    main()
    print("\n\nDone")
