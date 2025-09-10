from __future__ import annotations

from typing import Any, List, Optional

from services.db import fetch_all


def search_similar_chunks(
    *,
    query_vector: list[float],
    job_id: Optional[str] = None,
    candidate_id: Optional[str] = None,
    section: Optional[str] = None,
    limit: int = 5,
    similarity_threshold: float = 0.6,
):
    # Use SQL function if present; else inline query
    params: list[Any] = []
    where = []
    if job_id:
        where.append("c.job_id = %s"); params.append(job_id)
    if candidate_id:
        where.append("c.candidate_id = %s"); params.append(candidate_id)
    if section:
        where.append("c.section = %s"); params.append(section)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    sql = f'''
        SELECT c.id as chunk_id, c.content, c.section, c.heading,
               1 - (e.vector <=> %s::vector) as similarity,
               d.title as document_title
        FROM chunks c
        JOIN embeddings e ON c.id = e.chunk_id
        JOIN documents d ON c.document_id = d.id
        {where_sql}
        ORDER BY e.vector <=> %s::vector
        LIMIT %s
    '''
    # Vector needs to be cast; we'll pass as tuple/list and rely on psycopg2 adaptation
    params2 = [query_vector, *params, query_vector, limit]
    # Fallback: we can also use the SQL function search_similar_chunks if needed
    return fetch_all(sql, tuple(params2))


def hybrid_search_chunks(
    *,
    query_vector: list[float],
    query_text: str,
    job_id: Optional[str] = None,
    candidate_id: Optional[str] = None,
    section: Optional[str] = None,
    limit: int = 5,
):
    params: list[Any] = []
    where = ["to_tsvector('english', c.content) @@ plainto_tsquery('english', %s)"]
    params.append(query_text)
    if job_id:
        where.append("c.job_id = %s"); params.append(job_id)
    if candidate_id:
        where.append("c.candidate_id = %s"); params.append(candidate_id)
    if section:
        where.append("c.section = %s"); params.append(section)
    where_sql = "WHERE " + " AND ".join(where)
    sql = f'''
        SELECT c.id as chunk_id, c.content, c.section, c.heading,
               1 - (e.vector <=> %s::vector) as vector_similarity,
               ts_rank(to_tsvector('english', c.content), plainto_tsquery('english', %s)) as text_rank,
               d.title as document_title
        FROM chunks c
        JOIN embeddings e ON c.id = e.chunk_id
        JOIN documents d ON c.document_id = d.id
        {where_sql}
        ORDER BY (1 - (e.vector <=> %s::vector)) * 0.7 + ts_rank(to_tsvector('english', c.content), plainto_tsquery('english', %s)) * 0.3 DESC
        LIMIT %s
    '''
    params2 = [query_vector, query_text, *params, query_vector, query_text, limit]
    return fetch_all(sql, tuple(params2))

