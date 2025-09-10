-- Indexes for performance and search

-- Candidates indexes
CREATE INDEX idx_candidates_email ON candidates(email) WHERE email IS NOT NULL;
CREATE INDEX idx_candidates_phone ON candidates(phone) WHERE phone IS NOT NULL;

-- Jobs indexes
CREATE INDEX idx_jobs_team ON jobs(team);
CREATE INDEX idx_jobs_seniority ON jobs(seniority);
CREATE INDEX idx_jobs_location ON jobs(location);

-- Documents indexes
CREATE INDEX idx_documents_job_id ON documents(job_id);
CREATE INDEX idx_documents_source_type ON documents(source_type);
CREATE INDEX idx_documents_active ON documents(is_active);
CREATE INDEX idx_documents_job_source ON documents(job_id, source_type, is_active);

-- Chunks indexes
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chunks_job_id ON chunks(job_id);
CREATE INDEX idx_chunks_candidate_id ON chunks(candidate_id);
CREATE INDEX idx_chunks_section ON chunks(section);
CREATE INDEX idx_chunks_job_section ON chunks(job_id, section);
CREATE INDEX idx_chunks_candidate_section ON chunks(candidate_id, section);

-- Full-text search index on chunks content
CREATE INDEX idx_chunks_content_gin ON chunks USING gin(to_tsvector('english', content));

-- Embeddings vector index (HNSW for similarity search)
CREATE INDEX idx_embeddings_vector_hnsw ON embeddings USING hnsw (vector vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Alternative IVFFLAT index (uncomment if HNSW doesn't work)
-- CREATE INDEX idx_embeddings_vector_ivfflat ON embeddings USING ivfflat (vector vector_cosine_ops)
-- WITH (lists = 100);

-- Screenings indexes
CREATE INDEX idx_screenings_candidate_id ON screenings(candidate_id);
CREATE INDEX idx_screenings_job_id ON screenings(job_id);
CREATE INDEX idx_screenings_fit_score ON screenings(fit_score);

-- Conversations indexes
CREATE INDEX idx_conversations_candidate_id ON conversations(candidate_id);
CREATE INDEX idx_conversations_job_id ON conversations(job_id);
CREATE INDEX idx_conversations_status ON conversations(status);

-- Messages indexes
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
