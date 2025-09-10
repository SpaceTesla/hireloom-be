-- Create enums
CREATE TYPE source_type AS ENUM ('resume', 'jd', 'faq', 'company', 'process');
CREATE TYPE section_type AS ENUM ('experience', 'skills', 'projects', 'education', 'certs', 'requirements', 'responsibilities', 'benefits', 'faq', 'about_company', 'process', 'other');
CREATE TYPE conversation_status AS ENUM ('active', 'scheduled', 'closed');
CREATE TYPE interest_level AS ENUM ('unknown', 'interested', 'not_interested');
CREATE TYPE message_sender AS ENUM ('agent', 'candidate', 'system');

-- Candidates table
CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    location TEXT,
    linkedin_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    team TEXT,
    seniority TEXT,
    location TEXT,
    employment_type TEXT,
    compensation_range TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table (resumes, JDs, FAQs, company docs)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    source_type source_type NOT NULL,
    title TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chunks table (segmented content from documents)
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    section section_type NOT NULL,
    heading TEXT,
    content TEXT NOT NULL,
    token_count INTEGER,
    position INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Embeddings table (vector storage)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID UNIQUE NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    model TEXT NOT NULL DEFAULT 'gemini-embedding-001',
    dim INTEGER NOT NULL DEFAULT 768 CHECK (dim = 768),
    vector vector(768) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Screenings table (RAG-based screening results)
CREATE TABLE screenings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    fit_score DECIMAL(3,2) CHECK (fit_score >= 0 AND fit_score <= 1),
    summary TEXT,
    evidence JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(candidate_id, job_id)
);

-- Conversations table (for future chat functionality)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status conversation_status DEFAULT 'active',
    interest interest_level DEFAULT 'unknown',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table (for future chat functionality)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender message_sender NOT NULL,
    text TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
