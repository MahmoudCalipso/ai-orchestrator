"""SQLAlchemy models for Agents."""
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, Enum as SQLEnum
import enum
from datetime import datetime
import uuid
from ..core.database import Base

class AgentStatus(str, enum.Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"
    ARCHIVED = "archived"

class AgentType(str, enum.Enum):
    ORCHESTRATOR = "orchestrator"
    CODE_GENERATOR = "code_generator"
    CODE_REVIEWER = "code_reviewer"
    DEBUGGER = "debugger"
    DOCUMENTATION = "documentation"
    ANALYZER = "analyzer"
    SECURITY = "security"
    OPTIMIZER = "optimizer"
    CUSTOM = "custom"

class Agent(Base):
    """SQLAlchemy model for AI Agents."""
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    agent_type = Column(SQLEnum(AgentType), nullable=False, index=True)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.INITIALIZING, index=True)
    
    # Model Configuration
    model = Column(String(50), default="gpt-4o")
    system_prompt = Column(String, nullable=True)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    tools = Column(JSON, default=list)
    
    # Metadata & Statistics
    session_count = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    metadata_ = Column("metadata", JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
