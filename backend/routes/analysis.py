from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from typing import List, Dict, Any

from backend.models.schemas import (
    CaseAnalysisRequest,
    CaseAnalysisResponse,
    DocumentUploadResponse,
    SampleCaseItem
)
from backend.services.jurisai_engine import get_engine, JurisAIEngine

router = APIRouter(prefix="/api", tags=["Legal Case Analysis"])

@router.get("/health")
def health_check(engine: JurisAIEngine = Depends(get_engine)):
    return {
        "status": "healthy",
        "service": "JurisAI Legal Reasoning Backend",
        "acts_covered": 12,
        "precedents_indexed": 91,
        "chroma_master_chunks": engine.vector_store.master_col.count(),
        "chroma_statute_chunks": engine.vector_store.statute_col.count(),
        "chroma_precedent_chunks": engine.vector_store.precedent_col.count(),
        "agents_available": [
            "CaseManagerAgent",
            "LawAgent",
            "PrecedentAgent",
            "EvidenceAgent",
            "ConstraintHunterAgent",
            "OppositionAgent",
            "AuditorAgent",
            "JudgeAgent"
        ]
    }

@router.get("/sample-cases", response_model=List[SampleCaseItem])
def get_sample_cases(engine: JurisAIEngine = Depends(get_engine)):
    return engine.get_sample_cases()

@router.post("/analyze", response_model=CaseAnalysisResponse)
def analyze_case(request: CaseAnalysisRequest, req: Request, engine: JurisAIEngine = Depends(get_engine)):
    if not request.case_text.strip():
        raise HTTPException(status_code=400, detail="Case description cannot be empty.")
    try:
        req_analysis_id = req.headers.get("X-Analysis-ID")
        result = engine.analyze_case(
            case_text=request.case_text,
            uploaded_docs=request.uploaded_documents,
            inject_fault=request.inject_fault,
            analysis_id=req_analysis_id
        )

        # If user is authenticated, automatically record into their search/analysis history
        auth_header = req.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            try:
                import json
                from backend.services.auth_service import get_auth_service
                auth_svc = get_auth_service()
                user = auth_svc.get_user_by_token(token)
                if user:
                    case_type = result.get("case_state", {}).get("case_type", "Legal Case Analysis")
                    cleaned_summary = request.case_text.strip()[:140] + ("..." if len(request.case_text.strip()) > 140 else "")
                    auth_svc.save_history(
                        user_id=user["id"],
                        query_text=request.case_text.strip(),
                        case_type=case_type,
                        outcome=result.get("outcome", "PASS"),
                        summary=cleaned_summary,
                        analysis_id=result.get("analysis_id"),
                        analysis_data_json=json.dumps(result)
                    )
            except Exception:
                pass  # Gracefully continue even if history logging encounters an issue

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")

@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...), engine: JurisAIEngine = Depends(get_engine)):
    try:
        content = await file.read()
        res = engine.parse_document(file.filename or "uploaded_doc.txt", content)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document parsing error: {str(e)}")
