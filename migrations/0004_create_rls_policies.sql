-- Enable Row Level Security
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE screenings ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Service role policies (full access for backend)
CREATE POLICY "Service role full access on candidates" ON candidates
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on jobs" ON jobs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on documents" ON documents
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on chunks" ON chunks
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on embeddings" ON embeddings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on screenings" ON screenings
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on conversations" ON conversations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on messages" ON messages
    FOR ALL USING (auth.role() = 'service_role');

-- Anonymous policies (deny by default for now)
-- These can be updated later for public read access if needed

-- Optional: Public read access for documents/chunks (uncomment if needed for demos)
-- CREATE POLICY "Public read access on documents" ON documents
--     FOR SELECT USING (true);
-- 
-- CREATE POLICY "Public read access on chunks" ON chunks
--     FOR SELECT USING (true);
