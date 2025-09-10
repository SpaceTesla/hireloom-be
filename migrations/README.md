# Database Migrations

This directory contains SQL migrations for setting up the HireLoom RAG-based screening system.

## Migration Order

1. `0001_enable_extensions.sql` - Enable required PostgreSQL extensions
2. `0002_create_tables.sql` - Create all tables and enums
3. `0003_create_indexes.sql` - Create performance and search indexes
4. `0004_create_rls_policies.sql` - Set up Row Level Security policies
5. `0005_create_functions.sql` - Create utility functions for RAG operations

## Running Migrations

### Using Supabase CLI

```bash
supabase db reset
# or
supabase db push
```

### Using psql

```bash
psql -h your-supabase-host -U postgres -d postgres -f migrations/0001_enable_extensions.sql
psql -h your-supabase-host -U postgres -d postgres -f migrations/0002_create_tables.sql
psql -h your-supabase-host -U postgres -d postgres -f migrations/0003_create_indexes.sql
psql -h your-supabase-host -U postgres -d postgres -f migrations/0004_create_rls_policies.sql
psql -h your-supabase-host -U postgres -d postgres -f migrations/0005_create_functions.sql
```

## Key Features

- **Vector Search**: Uses pgvector with 768-dimensional Gemini embeddings
- **Hybrid Search**: Combines vector similarity with full-text search
- **RLS Security**: Row-level security for multi-tenant support
- **Performance**: Optimized indexes for fast retrieval
- **Flexibility**: Supports multiple document types and sections

## Schema Overview

- `candidates` - Basic candidate information
- `jobs` - Job postings and requirements
- `documents` - Raw documents (resumes, JDs, FAQs)
- `chunks` - Segmented content from documents
- `embeddings` - Vector embeddings for semantic search
- `screenings` - RAG-based screening results
- `conversations` - Chat conversations (future)
- `messages` - Chat messages (future)
