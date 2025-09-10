from __future__ import annotations

from typing import Dict, List, Optional, Tuple
import re

from services.embeddings import embed_texts
from services.retrieval import search_similar_chunks, hybrid_search_chunks
from services.db import fetch_all, fetch_one_commit, fetch_one
from psycopg2.extras import Json


TECH_SKILLS = {
    # frontend
    "react", "next.js", "nextjs", "typescript", "javascript", "tailwind", "redux", "vite", "webpack",
    # backend
    "node", "express", "fastapi", "flask", "django", "go", "gin", "python",
    # db/devops
    "postgresql", "postgres", "mysql", "mongodb", "prisma", "docker", "kubernetes", "aws", "gcp", "cloudflare",
}

ALIASES = {
    "nextjs": "next.js",
    "js": "javascript",
    "ts": "typescript",
    "postgres": "postgresql",
}


def _normalize_skill(token: str) -> str:
    k = token.lower()
    return ALIASES.get(k, k)


def _extract_skills(text: str) -> List[str]:
    # crude skill extraction: keep tokens with letters, dots, plus signs, and hashes
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9.+#/-]{1,}\b", text)
    norm = {_normalize_skill(t) for t in tokens}
    skills = [s for s in norm if s in TECH_SKILLS]
    return sorted(set(skills))


def _extract_must_have_skills(requirements_texts: List[str]) -> List[str]:
    text = "\n".join(requirements_texts)
    skills = _extract_skills(text)
    return skills


def _extract_skills_from_job_title_and_intro(job_title: str, jd_text: str) -> List[str]:
    # Extract from job title + first 200 chars of JD
    title_skills = _extract_skills(job_title)
    intro_skills = _extract_skills(jd_text[:200])
    return list(set(title_skills + intro_skills))[:5]  # top 5 skills


def _fetch_jd_targets(job_id: str) -> Dict[str, List[str]]:
    # Pull JD chunks grouped by section for targeting
    rows = fetch_all(
        "SELECT section, content FROM chunks WHERE job_id = %s ORDER BY position",
        (job_id,),
    )
    sections: Dict[str, List[str]] = {}
    for r in rows:
        sec = r["section"]
        sections.setdefault(sec, []).append(r["content"])
    return sections


def _score_by_similarity(resume_hits: List[dict]) -> float:
    if not resume_hits:
        return 0.0
    sims = [float(h.get("similarity", 0.0)) for h in resume_hits]
    return round(sum(sims) / len(sims), 4)


def _extract_years_experience(resume_text: str) -> float:
    # Look for patterns like "2 years", "3+ years", "6 months"
    patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
        r'(\d+)\s*months?',
        r'(\d+(?:\.\d+)?)\+\s*years?'
    ]
    
    years = 0.0
    for pattern in patterns:
        matches = re.findall(pattern, resume_text.lower())
        for match in matches:
            if 'month' in pattern:
                years += float(match) / 12
            else:
                years += float(match)
    
    return min(years, 20.0)  # cap at 20 years


def _assess_seniority_level(resume_text: str) -> str:
    senior_keywords = ['senior', 'lead', 'principal', 'architect', 'manager', 'director', 'cto', 'vp']
    mid_keywords = ['mid', 'intermediate', 'experienced']
    junior_keywords = ['junior', 'entry', 'graduate', 'intern', 'trainee']
    
    text_lower = resume_text.lower()
    
    if any(keyword in text_lower for keyword in senior_keywords):
        return 'senior'
    elif any(keyword in text_lower for keyword in mid_keywords):
        return 'mid'
    elif any(keyword in text_lower for keyword in junior_keywords):
        return 'junior'
    else:
        # Infer from experience years
        years = _extract_years_experience(resume_text)
        if years >= 5:
            return 'senior'
        elif years >= 2:
            return 'mid'
        else:
            return 'junior'


def run_screening(*, job_id: str, candidate_id: str) -> Dict:
    # Get job details
    job_row = fetch_one("SELECT title, team, seniority, location FROM jobs WHERE id = %s", (job_id,))
    job_title = job_row["title"] if job_row else ""
    job_team = job_row["team"] if job_row else ""
    job_seniority = job_row["seniority"] if job_row else ""
    job_location = job_row["location"] if job_row else ""
    
    # Get candidate details
    candidate_row = fetch_one("SELECT full_name, location FROM candidates WHERE id = %s", (candidate_id,))
    candidate_name = candidate_row["full_name"] if candidate_row else ""
    candidate_location = candidate_row["location"] if candidate_row else ""
    
    # Get JD content
    jd_sections = _fetch_jd_targets(job_id)
    all_jd_text = "\n".join(jd_sections.get("requirements", []) + jd_sections.get("responsibilities", []) + jd_sections.get("other", []))
    
    # Get resume content
    resume_chunks = fetch_all(
        "SELECT content FROM chunks WHERE candidate_id = %s ORDER BY position",
        (candidate_id,)
    )
    resume_text = "\n".join([chunk["content"] for chunk in resume_chunks])
    
    # 1. Technical Skills Assessment
    jd_skills = _extract_skills(all_jd_text)
    resume_skills = _extract_skills(resume_text)
    
    # Find matching skills
    matching_skills = [skill for skill in jd_skills if skill in resume_skills]
    missing_skills = [skill for skill in jd_skills if skill not in resume_skills]
    
    skills_score = len(matching_skills) / len(jd_skills) if jd_skills else 0.0
    
    # 2. Experience Level Assessment
    resume_years = _extract_years_experience(resume_text)
    candidate_seniority = _assess_seniority_level(resume_text)
    
    # Match seniority expectations
    seniority_match = 1.0
    if job_seniority:
        if job_seniority.lower() == 'senior' and candidate_seniority != 'senior':
            seniority_match = 0.3
        elif job_seniority.lower() == 'mid' and candidate_seniority == 'junior':
            seniority_match = 0.5
        elif job_seniority.lower() == 'junior' and candidate_seniority == 'senior':
            seniority_match = 0.7  # Overqualified but still relevant
    
    # 3. Domain/Industry Relevance
    domain_keywords = ['frontend', 'backend', 'full-stack', 'mobile', 'web', 'api', 'database', 'cloud', 'devops']
    jd_domain = [kw for kw in domain_keywords if kw in all_jd_text.lower()]
    resume_domain = [kw for kw in domain_keywords if kw in resume_text.lower()]
    
    domain_score = len(set(jd_domain) & set(resume_domain)) / len(jd_domain) if jd_domain else 0.5
    
    # 4. Location Match
    location_score = 1.0
    if job_location and candidate_location:
        if job_location.lower() in candidate_location.lower() or candidate_location.lower() in job_location.lower():
            location_score = 1.0
        elif 'remote' in job_location.lower() or 'remote' in candidate_location.lower():
            location_score = 0.8
        else:
            location_score = 0.3
    
    # 5. Overall Experience Relevance (semantic similarity)
    if all_jd_text and resume_text:
        jd_vec = embed_texts([all_jd_text])[0]
        resume_hits = search_similar_chunks(query_vector=jd_vec, candidate_id=candidate_id, limit=10)
        experience_score = _score_by_similarity(resume_hits)
    else:
        experience_score = 0.0
    
    # Calculate weighted overall score
    weights = {
        "skills": 0.35,
        "seniority": 0.20,
        "domain": 0.15,
        "location": 0.10,
        "experience": 0.20
    }
    
    overall_score = (
        skills_score * weights["skills"] +
        seniority_match * weights["seniority"] +
        domain_score * weights["domain"] +
        location_score * weights["location"] +
        experience_score * weights["experience"]
    )
    
    # Determine recommendation
    if overall_score >= 0.8:
        recommendation = "Strong Hire"
    elif overall_score >= 0.6:
        recommendation = "Hire"
    elif overall_score >= 0.4:
        recommendation = "Maybe"
    else:
        recommendation = "Pass"
    
    # Generate summary
    summary_parts = [
        f"Skills: {len(matching_skills)}/{len(jd_skills)} matched",
        f"Seniority: {candidate_seniority} vs {job_seniority or 'any'}",
        f"Experience: {resume_years:.1f} years",
        f"Location: {'Match' if location_score > 0.7 else 'Mismatch'}"
    ]
    summary = f"{recommendation} ({overall_score:.2f}) - " + ", ".join(summary_parts)
    
    # Prepare evidence
    evidence = {
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "candidate_seniority": candidate_seniority,
        "job_seniority": job_seniority,
        "experience_years": resume_years,
        "domain_match": list(set(jd_domain) & set(resume_domain)),
        "location_match": location_score > 0.7,
        "resume_evidence": resume_hits[:5] if 'resume_hits' in locals() else []
    }
    
    # Store results
    row = fetch_one_commit(
        "INSERT INTO screenings (candidate_id, job_id, fit_score, summary, evidence) VALUES (%s, %s, %s, %s, %s) "
        "ON CONFLICT (candidate_id, job_id) DO UPDATE SET fit_score=EXCLUDED.fit_score, summary=EXCLUDED.summary, evidence=EXCLUDED.evidence RETURNING id",
        (candidate_id, job_id, overall_score, summary, Json(evidence)),
    )
    
    return {
        "screening_id": row["id"],
        "fit_score": round(overall_score, 4),
        "recommendation": recommendation,
        "criteria": {
            "skills_match": f"{len(matching_skills)}/{len(jd_skills)}",
            "seniority": f"{candidate_seniority} vs {job_seniority or 'any'}",
            "experience_years": resume_years,
            "domain_relevance": domain_score,
            "location_match": location_score > 0.7
        },
        "summary": summary,
        "evidence": evidence
    }


