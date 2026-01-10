"""
Database Schema for Framework Registry
Stores framework versions, SDKs, JDKs, and metadata
"""

CREATE_FRAMEWORK_REGISTRY_TABLES = """
-- Framework Versions Table
CREATE TABLE IF NOT EXISTS framework_versions (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    framework VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    is_latest BOOLEAN DEFAULT FALSE,
    is_lts BOOLEAN DEFAULT FALSE,
    is_deprecated BOOLEAN DEFAULT FALSE,
    release_date DATE,
    end_of_life_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, framework, version)
);

-- SDK/JDK Versions Table
CREATE TABLE IF NOT EXISTS sdk_versions (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    sdk_type VARCHAR(50) NOT NULL,  -- 'SDK', 'JDK', 'Runtime'
    version VARCHAR(50) NOT NULL,
    is_latest BOOLEAN DEFAULT FALSE,
    is_lts BOOLEAN DEFAULT FALSE,
    release_date DATE,
    end_of_support_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, sdk_type, version)
);

-- Framework Best Practices Table
CREATE TABLE IF NOT EXISTS framework_best_practices (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    framework VARCHAR(100) NOT NULL,
    practice TEXT NOT NULL,
    category VARCHAR(50),  -- 'security', 'performance', 'architecture', etc.
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Framework Required Packages Table
CREATE TABLE IF NOT EXISTS framework_packages (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    framework VARCHAR(100) NOT NULL,
    package_name VARCHAR(200) NOT NULL,
    package_version VARCHAR(50),
    is_required BOOLEAN DEFAULT TRUE,
    category VARCHAR(50),  -- 'core', 'database', 'auth', 'testing', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, framework, package_name)
);

-- Architecture Patterns Table
CREATE TABLE IF NOT EXISTS architecture_patterns (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    framework VARCHAR(100) NOT NULL,
    pattern_name VARCHAR(100) NOT NULL,  -- 'MVP', 'MVC', 'Clean Architecture', etc.
    description TEXT,
    is_recommended BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, framework, pattern_name)
);

-- Registry Update Log Table
CREATE TABLE IF NOT EXISTS registry_update_log (
    id SERIAL PRIMARY KEY,
    update_type VARCHAR(50) NOT NULL,  -- 'framework', 'sdk', 'package'
    language VARCHAR(50),
    framework VARCHAR(100),
    old_version VARCHAR(50),
    new_version VARCHAR(50),
    source VARCHAR(100),  -- 'PyPI', 'npm', 'Maven', 'NuGet'
    status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'applied', 'failed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Top Frameworks/Tags Table (Top 5)
CREATE TABLE IF NOT EXISTS top_frameworks (
    id SERIAL PRIMARY KEY,
    language VARCHAR(50) NOT NULL,
    framework VARCHAR(100) NOT NULL,
    rank INTEGER NOT NULL,
    downloads_count BIGINT,
    github_stars INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, rank)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_framework_versions_language ON framework_versions(language);
CREATE INDEX IF NOT EXISTS idx_framework_versions_framework ON framework_versions(framework);
CREATE INDEX IF NOT EXISTS idx_framework_versions_latest ON framework_versions(is_latest);
CREATE INDEX IF NOT EXISTS idx_sdk_versions_language ON sdk_versions(language);
CREATE INDEX IF NOT EXISTS idx_framework_packages_language_framework ON framework_packages(language, framework);
CREATE INDEX IF NOT EXISTS idx_top_frameworks_language ON top_frameworks(language);
CREATE INDEX IF NOT EXISTS idx_registry_update_log_created_at ON registry_update_log(created_at);
"""


class FrameworkDatabaseManager:
    """Manage framework registry database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def initialize_schema(self):
        """Initialize database schema"""
        await self.db.execute(CREATE_FRAMEWORK_REGISTRY_TABLES)
    
    async def save_framework_version(
        self,
        language: str,
        framework: str,
        version: str,
        is_latest: bool = False,
        is_lts: bool = False,
        release_date: str = None
    ):
        """Save framework version to database"""
        query = """
        INSERT INTO framework_versions 
        (language, framework, version, is_latest, is_lts, release_date)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (language, framework, version) 
        DO UPDATE SET 
            is_latest = EXCLUDED.is_latest,
            is_lts = EXCLUDED.is_lts,
            updated_at = CURRENT_TIMESTAMP
        """
        await self.db.execute(
            query,
            language,
            framework,
            version,
            is_latest,
            is_lts,
            release_date
        )
    
    async def save_sdk_version(
        self,
        language: str,
        sdk_type: str,
        version: str,
        is_latest: bool = False,
        is_lts: bool = False
    ):
        """Save SDK/JDK version"""
        query = """
        INSERT INTO sdk_versions 
        (language, sdk_type, version, is_latest, is_lts)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (language, sdk_type, version)
        DO UPDATE SET
            is_latest = EXCLUDED.is_latest,
            is_lts = EXCLUDED.is_lts,
            updated_at = CURRENT_TIMESTAMP
        """
        await self.db.execute(query, language, sdk_type, version, is_latest, is_lts)
    
    async def save_best_practices(
        self,
        language: str,
        framework: str,
        practices: list
    ):
        """Save best practices"""
        for practice in practices:
            query = """
            INSERT INTO framework_best_practices 
            (language, framework, practice)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
            """
            await self.db.execute(query, language, framework, practice)
    
    async def save_required_packages(
        self,
        language: str,
        framework: str,
        packages: list
    ):
        """Save required packages"""
        for package in packages:
            query = """
            INSERT INTO framework_packages 
            (language, framework, package_name, is_required)
            VALUES ($1, $2, $3, TRUE)
            ON CONFLICT (language, framework, package_name) DO NOTHING
            """
            await self.db.execute(query, language, framework, package)
    
    async def get_latest_version(
        self,
        language: str,
        framework: str
    ) -> str:
        """Get latest framework version"""
        query = """
        SELECT version FROM framework_versions
        WHERE language = $1 AND framework = $2 AND is_latest = TRUE
        LIMIT 1
        """
        result = await self.db.fetchrow(query, language, framework)
        return result['version'] if result else None
    
    async def get_top_frameworks(
        self,
        language: str,
        limit: int = 5
    ) -> list:
        """Get top frameworks for language"""
        query = """
        SELECT framework, rank, downloads_count, github_stars
        FROM top_frameworks
        WHERE language = $1
        ORDER BY rank
        LIMIT $2
        """
        results = await self.db.fetch(query, language, limit)
        return [dict(row) for row in results]
    
    async def log_update(
        self,
        update_type: str,
        language: str,
        framework: str,
        old_version: str,
        new_version: str,
        source: str
    ):
        """Log registry update"""
        query = """
        INSERT INTO registry_update_log
        (update_type, language, framework, old_version, new_version, source)
        VALUES ($1, $2, $3, $4, $5, $6)
        """
        await self.db.execute(
            query,
            update_type,
            language,
            framework,
            old_version,
            new_version,
            source
        )
