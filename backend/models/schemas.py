from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class CaseAnalysisRequest(BaseModel):
    case_text: str = Field(..., description="Raw narrative of the matrimonial dispute")
    uploaded_documents: Optional[List[str]] = Field(default=[], description="Extracted texts from uploaded documents")
    sub_case_type: Optional[str] = Field(default=None, description="Optional hinted sub-case category")
    inject_fault: Optional[str] = Field(default=None, description="Testing parameter for deliberate fault injection")

class AuditErrorSchema(BaseModel):
    type: str
    responsible_agent: str
    description: str
    severity: str
    evidence_or_source: str
    recommended_fix: str

class AuditReportSchema(BaseModel):
    iteration: int
    audit_status: str
    errors: List[AuditErrorSchema]
    reanalysis_required: bool
    citation_verifications: List[Dict[str, Any]]
    summary: str

class CaseAnalysisResponse(BaseModel):
    analysis_id: Optional[str] = Field(default=None, description="Unique trace identifier for this case analysis execution")
    case_state: Dict[str, Any]
    outcome: str
    total_iterations: int
    audit_history: List[AuditReportSchema]
    agent_outputs: Dict[str, Any]
    final_judgment: str
    elapsed_seconds: float

class DocumentUploadResponse(BaseModel):
    filename: str
    extracted_text: str
    char_count: int
    detected_entities: List[str]

class SampleCaseItem(BaseModel):
    id: str
    title: str
    category: str
    facts_summary: str
    full_text: str
    engineering_notes: str

# ------------------------------------------------------------------------------
# Authentication & Search History Schemas
# ------------------------------------------------------------------------------
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: str = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (at least 6 characters)")
    full_name: Optional[str] = Field(default=None, description="Optional full name or title")

class UserLoginRequest(BaseModel):
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: str

class AuthResponse(BaseModel):
    user: UserProfile
    token: str
    message: str = "Authentication successful"

class HistoryItemSummary(BaseModel):
    id: int
    analysis_id: Optional[str] = None
    query_text: str
    case_type: Optional[str] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    created_at: str

class HistoryDetailResponse(BaseModel):
    id: int
    analysis_id: Optional[str] = None
    query_text: str
    case_type: Optional[str] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
    created_at: str

class SaveHistoryRequest(BaseModel):
    query_text: str
    case_type: Optional[str] = None
    outcome: Optional[str] = None
    summary: Optional[str] = None
    analysis_id: Optional[str] = None
    analysis_data: Optional[Dict[str, Any]] = None
