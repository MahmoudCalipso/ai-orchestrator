"""
DEPRECATED: Use dto/v1/ instead.
This file is kept for backward compatibility during active runtime switch-over.
"""
from dto.v1.requests.ai import (
    CodeTaskRequest, FixCodeRequest, AnalyzeCodeRequest,
    TestCodeRequest, OptimizeCodeRequest, DocumentCodeRequest,
    ReviewCodeRequest, ExplainCodeRequest, RefactorCodeRequest
)
from dto.v1.requests.project import (
    ProjectAnalyzeRequest, ProjectAddFeatureRequest
)
from dto.v1.requests.git import (
    GitConfigUpdate, GitRepoInit, GitRemoteCreate,
    GitBranchCreate, GitCommitRequest, GitConflictResolve,
    GitMergeRequest
)
from dto.v1.requests.generation import (
    WorkbenchCreateRequest, MigrationStartRequest,
    FigmaAnalyzeRequest, SecurityScanRequest
)
from dto.v1.requests.ide import (
    IDEWorkspaceRequest, IDEFileWriteRequest,
    IDETerminalRequest, IDEDebugRequest
)
from dto.v1.requests.workspace import (
    CollaborationSessionRequest, WorkspaceCreateRequest,
    WorkspaceInviteRequest
)
from dto.common.base_response import BaseResponse
from dto.v1.responses.swarm import SwarmResponse

# Aliases for backward compatibility if strict types were used
StandardResponse = BaseResponse 
PowerfulResponse = BaseResponse
PowerfulErrorResponse = BaseResponse
