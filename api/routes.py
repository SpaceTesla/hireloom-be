from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from fastapi.background import BackgroundTasks

from services.ingest_resume import ingest_resume, extract_text_from_pdf
from services.ingest_jd import ingest_jd
from services.db import fetch_one_commit, fetch_one, execute
from services.embeddings import embed_texts
from services.retrieval import search_similar_chunks
from services.screening import run_screening


router = APIRouter()


@router.post("/candidates")
def create_candidate(
    full_name: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    linkedin_url: Optional[str] = Form(None),
):
    row = fetch_one_commit(
        "INSERT INTO candidates (full_name, email, phone, location, linkedin_url) VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (full_name, email, phone, location, linkedin_url),
    )
    return {"candidate_id": row["id"]}


@router.post("/candidates/{candidate_id}/resumes:upload")
async def upload_resume(candidate_id: str, file: UploadFile = File(...)):
    # Ensure candidate exists in current DB
    exists = fetch_one("SELECT 1 AS ok FROM candidates WHERE id = %s", (candidate_id,))
    if not exists:
        return {"error": f"candidate_id {candidate_id} not found in database"}
    # Save to a temp file (delete=False) to avoid Windows file locking issues
    import tempfile, os
    content = await file.read()
    tmp_path: str = ""
    try:
        fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        # Ensure file handle is closed before PyMuPDF opens it
        text = extract_text_from_pdf(tmp_path)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    doc_id, num_chunks, num_vecs = ingest_resume(candidate_id=candidate_id, resume_title=file.filename, raw_text=text)
    return {"document_id": doc_id, "chunks": num_chunks, "embedded": num_vecs}


@router.post("/jobs/{job_id}/resumes:upload")
async def upload_resume_and_process(job_id: str, background: BackgroundTasks, file: UploadFile = File(...),
                                    full_name: Optional[str] = Form(None), email: Optional[str] = Form(None),
                                    phone: Optional[str] = Form(None), location: Optional[str] = Form(None),
                                    linkedin_url: Optional[str] = Form(None)):
    # Read file data immediately (before background processing)
    data = await file.read()
    
    # Create or upsert candidate (by email/phone if provided)
    if email:
        row = fetch_one("SELECT id FROM candidates WHERE email = %s", (email,))
    else:
        row = None
    if not row and phone:
        row = fetch_one("SELECT id FROM candidates WHERE phone = %s", (phone,))
    if row:
        candidate_id = row["id"]
        if full_name or location or linkedin_url:
            execute("UPDATE candidates SET full_name = COALESCE(%s, full_name), location = COALESCE(%s, location), linkedin_url = COALESCE(%s, linkedin_url) WHERE id = %s",
                    (full_name, location, linkedin_url, candidate_id))
    else:
        row = fetch_one_commit(
            "INSERT INTO candidates (full_name, email, phone, location, linkedin_url) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (full_name or "Unknown", email, phone, location, linkedin_url),
        )
        candidate_id = row["id"]

    # Create processing job
    pj = fetch_one_commit(
        "INSERT INTO processing_jobs (job_id, candidate_id, status, progress) VALUES (%s, %s, 'queued', 0) RETURNING id",
        (job_id, candidate_id),
    )
    processing_id = pj["id"]

    # Background task: extract, ingest, screen
    async def _process():
        tmp_path = None
        try:
            execute("UPDATE processing_jobs SET status='running', progress=10 WHERE id=%s", (processing_id,))
            
            # Write to temporary file
            import tempfile, os
            fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(data)
                # Ensure file is closed before processing
                f.close()
            except Exception as e:
                os.close(fd)
                raise e
                
            from services.ingest_resume import extract_text_from_pdf
            text = extract_text_from_pdf(tmp_path)

            # Extract candidate info from resume text
            import re
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
            phone_match = re.search(r'(\+?91[\s-]?)?[6-9]\d{9}', text)
            name_match = re.search(r'^#\s*\*\*([^*]+)\*\*', text, re.MULTILINE)
            
            extracted_email = email_match.group(0) if email_match else None
            extracted_phone = phone_match.group(0) if phone_match else None
            extracted_name = name_match.group(1).strip() if name_match else None
            
            # Update candidate with extracted info
            if extracted_name or extracted_email or extracted_phone:
                update_fields = []
                params = []
                if extracted_name:
                    update_fields.append("full_name = %s")
                    params.append(extracted_name)
                if extracted_email:
                    update_fields.append("email = %s")
                    params.append(extracted_email)
                if extracted_phone:
                    update_fields.append("phone = %s")
                    params.append(extracted_phone)
                
                if update_fields:
                    params.append(candidate_id)
                    execute(f"UPDATE candidates SET {', '.join(update_fields)} WHERE id = %s", tuple(params))

            # Ingest resume
            ingest_resume(candidate_id=candidate_id, resume_title=file.filename, raw_text=text)
            execute("UPDATE processing_jobs SET progress=60 WHERE id=%s", (processing_id,))

            # Run full RAG screening
            from services.screening import run_screening
            screening_result = run_screening(job_id=job_id, candidate_id=candidate_id)
            execute("UPDATE processing_jobs SET status='done', progress=100 WHERE id=%s", (processing_id,))
        except Exception as e:
            execute("UPDATE processing_jobs SET status='error', error_message=%s WHERE id=%s", (str(e), processing_id))
        finally:
            # Clean up temporary file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    background.add_task(_process)
    return {"processing_id": processing_id, "candidate_id": candidate_id}


@router.get("/processing/{processing_id}")
def get_processing_status(processing_id: str):
    row = fetch_one("SELECT id, job_id, candidate_id, status, progress, error_message, created_at, updated_at FROM processing_jobs WHERE id = %s", (processing_id,))
    if not row:
        return {"error": "not found"}
    return row


@router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    row = fetch_one("SELECT * FROM candidates WHERE id = %s", (candidate_id,))
    if not row:
        return {"error": "not found"}
    return row


@router.get("/candidates/{candidate_id}/screenings/{job_id}")
def get_screening(candidate_id: str, job_id: str):
    row = fetch_one("SELECT * FROM screenings WHERE candidate_id = %s AND job_id = %s", (candidate_id, job_id))
    if not row:
        return {"error": "not found"}
    return row


@router.post("/screenings:run")
def run_screening_endpoint(job_id: str = Form(...), candidate_id: str = Form(...)):
    return run_screening(job_id=job_id, candidate_id=candidate_id)


@router.post("/jobs")
def create_job(
    title: str = Form(...),
    team: Optional[str] = Form(None),
    seniority: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    employment_type: Optional[str] = Form(None),
    compensation_range: Optional[str] = Form(None),
):
    row = fetch_one_commit(
        "INSERT INTO jobs (title, team, seniority, location, employment_type, compensation_range) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (title, team, seniority, location, employment_type, compensation_range),
    )
    return {"job_id": row["id"]}


@router.post("/jobs/{job_id}/jd:upload")
async def upload_jd(job_id: str, title: str = Form(...), file: UploadFile = File(None), text: Optional[str] = Form(None)):
    if file is None and not text:
        return {"error": "Provide a JD file or text"}
    if file is not None:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
    assert text is not None
    doc_id, num_chunks, num_vecs = ingest_jd(job_id=job_id, title=title, text=text)
    return {"document_id": doc_id, "chunks": num_chunks, "embedded": num_vecs}

