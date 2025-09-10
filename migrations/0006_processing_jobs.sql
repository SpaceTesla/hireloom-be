-- Processing jobs table to track async resume analysis
CREATE TYPE processing_status AS ENUM ('queued', 'running', 'done', 'error');

CREATE TABLE processing_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    status processing_status NOT NULL DEFAULT 'queued',
    progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

ALTER TABLE processing_jobs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access on processing_jobs" ON processing_jobs
    FOR ALL USING (auth.role() = 'service_role');

CREATE INDEX idx_processing_jobs_job ON processing_jobs(job_id);
CREATE INDEX idx_processing_jobs_candidate ON processing_jobs(candidate_id);
CREATE INDEX idx_processing_jobs_status ON processing_jobs(status);

CREATE TRIGGER update_processing_jobs_updated_at BEFORE UPDATE ON processing_jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

