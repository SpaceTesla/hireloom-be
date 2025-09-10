from __future__ import annotations

from typing import Optional, Tuple

from services.db import execute_many, fetch_one_commit, fetch_all
from services.chunking import chunk_text
from services.embeddings import embed_texts, EMBEDDING_DIMENSION, EMBEDDING_MODEL_NAME


def _insert_document(job_id: str, title: str, raw_text: str) -> str:
    row = fetch_one_commit(
        "INSERT INTO documents (job_id, source_type, title, raw_text, version, is_active) VALUES (%s, 'jd', %s, %s, 1, true) RETURNING id",
        (job_id, title, raw_text),
    )
    return row["id"]


def _insert_chunks(document_id: str, job_id: str, chunks):
    query = (
        "INSERT INTO chunks (document_id, job_id, candidate_id, section, heading, content, token_count, position) "
        "VALUES (%s, %s, NULL, %s, %s, %s, %s, %s)"
    )
    params = []
    for ch in chunks:
        params.append((document_id, job_id, ch.section, ch.heading, ch.content, ch.token_count, ch.position))
    execute_many(query, params)


def _insert_embeddings_for_document(document_id: str) -> int:
    chunks = fetch_all(
        "SELECT id, content FROM chunks WHERE document_id = %s ORDER BY position",
        (document_id,),
    )
    texts = [r["content"] for r in chunks]
    vectors = embed_texts(texts)
    insert_q = (
        "INSERT INTO embeddings (chunk_id, model, dim, vector) VALUES (%s, %s, %s, %s)"
    )
    params = []
    for r, v in zip(chunks, vectors):
        params.append((r["id"], EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION, v))
    execute_many(insert_q, params)
    return len(params)


def ingest_jd(*, job_id: str, title: str, text: str) -> Tuple[str, int, int]:
    document_id = _insert_document(job_id, title, text)
    chunks = chunk_text(text)
    _insert_chunks(document_id, job_id, chunks)
    num_embedded = _insert_embeddings_for_document(document_id)
    return document_id, len(chunks), num_embedded

