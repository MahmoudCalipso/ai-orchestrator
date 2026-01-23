-- Database Initialization Script for AI Orchestrator
-- Target: PostgreSQL 16+

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 1. Users & Authentication
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    auth_provider VARCHAR(50),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. API Keys
CREATE TABLE IF NOT EXISTS api_keys (
    key_hash VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    rate_limit INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP
);

-- 3. Workspaces (Tenancy)
CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    owner_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workspace_members (
    workspace_id UUID REFERENCES workspaces(id) ON DELETE CASCADE,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (workspace_id, user_id)
);

-- 4. Projects & Generation
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    tech_stack JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_by VARCHAR(255) REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- 5. Migrations & Builds
CREATE TABLE IF NOT EXISTS migrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    source_stack JSONB NOT NULL,
    target_stack JSONB NOT NULL,
    status VARCHAR(50),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    result JSONB
);

CREATE TABLE IF NOT EXISTS builds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    build_number INTEGER,
    status VARCHAR(50),
    logs TEXT,
    artifacts JSONB,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_ms INTEGER
);

-- 6. Git Configuration
CREATE TABLE IF NOT EXISTS git_repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    provider VARCHAR(50) NOT NULL,
    repo_url TEXT NOT NULL,
    branch VARCHAR(255) DEFAULT 'main',
    credentials_encrypted TEXT,
    last_sync_at TIMESTAMP
);

-- 7. Audit & Metrics
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id VARCHAR(255) REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS usage_metrics (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value NUMERIC,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- 8. Neural Memory (Advanced Storage)
CREATE TABLE IF NOT EXISTS neural_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL, -- 'context', 'pattern', 'preference'
    content JSONB NOT NULL,
    confidence_score NUMERIC DEFAULT 1.0,
    accessed_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 9. Framework Registry (Original requirements)
CREATE TABLE IF NOT EXISTS framework_metadata (
    id BIGSERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    framework VARCHAR(50) NOT NULL,
    logo_url VARCHAR(255),
    latest_version VARCHAR(20),
    lts_version VARCHAR(20),
    versions JSONB DEFAULT '[]',
    architectures JSONB DEFAULT '[]',
    best_practices JSONB DEFAULT '[]',
    required_packages JSONB DEFAULT '[]',
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(language, framework)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_by ON projects(created_by);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_neural_memory_user_type ON neural_memory(user_id, memory_type);
CREATE INDEX IF NOT EXISTS idx_framework_registry_lang ON framework_metadata(language);

-- Full-text search index for projects
CREATE INDEX IF NOT EXISTS idx_projects_name_search ON projects USING gin(to_tsvector('english', name));
