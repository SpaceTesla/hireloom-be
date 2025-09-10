from __future__ import annotations

import hashlib
from typing import Optional, Tuple

from services.db import execute, fetch_one, fetch_one_commit, execute_many, fetch_all
from services.chunking import chunk_text
from services.embeddings import embed_texts, EMBEDDING_DIMENSION, EMBEDDING_MODEL_NAME

try:
    import pymupdf4llm
except Exception as exc:  # pragma: no cover
    raise RuntimeError("pymupdf4llm is required for PDF text extraction") from exc


def _insert_document(title: str, raw_text: str, source_type: str, candidate_id: Optional[str] = None) -> str:
    # For resumes, job_id is NULL
    query = (
        "INSERT INTO documents (job_id, source_type, title, raw_text, version, is_active) "
        "VALUES (NULL, %s, %s, %s, 1, true) RETURNING id"
    )
    row = fetch_one_commit(query, (source_type, title, raw_text))
    return row["id"]


def _insert_chunks(document_id: str, candidate_id: Optional[str], chunks):
    query = (
        "INSERT INTO chunks (document_id, job_id, candidate_id, section, heading, content, token_count, position) "
        "VALUES (%s, NULL, %s, %s, %s, %s, %s, %s) RETURNING id"
    )
    params = []
    for ch in chunks:
        params.append((document_id, candidate_id, ch.section, ch.heading, ch.content, ch.token_count, ch.position))
    execute_many(query, params)
    rows = fetch_one("SELECT COUNT(1) AS c FROM chunks WHERE document_id = %s", (document_id,))
    return rows["c"]


def _insert_embeddings_for_document(document_id: str) -> int:
    # Read back chunks for this document
    rows = fetch_one(
        "SELECT count(1) AS c FROM chunks WHERE document_id = %s",
        (document_id,),
    )
    # We will fetch in pages to embed
    # Simplify: embed in one go for now
    with_query = (
        "SELECT id, content FROM chunks WHERE document_id = %s ORDER BY position"
    )
    chunks = fetch_all(with_query, (document_id,))
    texts = [r["content"] for r in chunks]
    vectors = embed_texts(texts)
    assert len(vectors) == len(chunks)

    insert_q = (
        "INSERT INTO embeddings (chunk_id, model, dim, vector) VALUES (%s, %s, %s, %s)"
    )
    params = []
    for r, v in zip(chunks, vectors):
        params.append((r["id"], EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION, v))
    execute_many(insert_q, params)
    return len(params)


def extract_text_from_pdf(pdf_path: str) -> str:
    return pymupdf4llm.to_markdown(pdf_path)


def ingest_resume(
    *,
    candidate_id: Optional[str],
    resume_title: str,
    pdf_path: Optional[str] = None,
    raw_text: Optional[str] = None,
) -> Tuple[str, int, int]:
    if not (pdf_path or raw_text):
        raise ValueError("Provide either pdf_path or raw_text")

    text = raw_text or extract_text_from_pdf(pdf_path)  # type: ignore[arg-type]
    document_id = _insert_document(resume_title, text, source_type="resume", candidate_id=candidate_id)

    chunks = chunk_text(text)
    _insert_chunks(document_id, candidate_id, chunks)
    num_embedded = _insert_embeddings_for_document(document_id)
    return document_id, len(chunks), num_embedded

