from pydantic import BaseModel, Field

class CollaborationSessionRequest(BaseModel):
    """Request to create a collaboration session"""
    project_id: str
    owner_id: str
    owner_name: str

class WorkspaceCreateRequest(BaseModel):
    """Request to create a new user workspace"""
    name: str
    owner_id: str
    owner_name: str

class WorkspaceInviteRequest(BaseModel):
    """Request to invite a member to a workspace"""
    inviter_id: str
    user_id: str
    username: str
    role: str = "developer"
