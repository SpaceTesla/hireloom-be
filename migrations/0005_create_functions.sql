-- Utility functions for the RAG system

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_candidates_updated_at BEFORE UPDATE ON candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate token count (rough estimate)
CREATE OR REPLACE FUNCTION estimate_token_count(text_content TEXT)
RETURNS INTEGER AS $$
BEGIN
    -- Rough estimate: 1 token ≈ 4 characters for English text
    RETURN GREATEST(1, LENGTH(text_content) / 4);
END;
$$ LANGUAGE plpgsql;

-- Function to search similar chunks using vector similarity
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_vector vector(768),
    match_job_id UUID DEFAULT NULL,
    match_candidate_id UUID DEFAULT NULL,
    match_section section_type DEFAULT NULL,
    limit_count INTEGER DEFAULT 10,
    similarity_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    chunk_id UUID,
    content TEXT,
    section section_type,
    heading TEXT,
    similarity FLOAT,
    document_title TEXT,
    job_title TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id as chunk_id,
        c.content,
        c.section,
        c.heading,
        1 - (e.vector <=> query_vector) as similarity,
        d.title as document_title,
        j.title as job_title
    FROM chunks c
    JOIN embeddings e ON c.id = e.chunk_id
    JOIN documents d ON c.document_id = d.id
    LEFT JOIN jobs j ON c.job_id = j.id
    WHERE 
        (match_job_id IS NULL OR c.job_id = match_job_id)
        AND (match_candidate_id IS NULL OR c.candidate_id = match_candidate_id)
        AND (match_section IS NULL OR c.section = match_section)
        AND (1 - (e.vector <=> query_vector)) >= similarity_threshold
    ORDER BY e.vector <=> query_vector
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to search chunks with hybrid search (vector + text)
CREATE OR REPLACE FUNCTION hybrid_search_chunks(
    query_vector vector(768),
    query_text TEXT,
    match_job_id UUID DEFAULT NULL,
    match_candidate_id UUID DEFAULT NULL,
    match_section section_type DEFAULT NULL,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    chunk_id UUID,
    content TEXT,
    section section_type,
    heading TEXT,
    vector_similarity FLOAT,
    text_rank FLOAT,
    combined_score FLOAT,
    document_title TEXT,
    job_title TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id as chunk_id,
        c.content,
        c.section,
        c.heading,
        1 - (e.vector <=> query_vector) as vector_similarity,
        ts_rank(to_tsvector('english', c.content), plainto_tsquery('english', query_text)) as text_rank,
        (1 - (e.vector <=> query_vector)) * 0.7 + 
        ts_rank(to_tsvector('english', c.content), plainto_tsquery('english', query_text)) * 0.3 as combined_score,
        d.title as document_title,
        j.title as job_title
    FROM chunks c
    JOIN embeddings e ON c.id = e.chunk_id
    JOIN documents d ON c.document_id = d.id
    LEFT JOIN jobs j ON c.job_id = j.id
    WHERE 
        (match_job_id IS NULL OR c.job_id = match_job_id)
        AND (match_candidate_id IS NULL OR c.candidate_id = match_candidate_id)
        AND (match_section IS NULL OR c.section = match_section)
        AND to_tsvector('english', c.content) @@ plainto_tsquery('english', query_text)
    ORDER BY combined_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
