import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserProfile,
    AuthResponse,
    HistoryItemSummary,
    HistoryDetailResponse,
    SaveHistoryRequest
)
from backend.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/api", tags=["Authentication & Search History"])
security = HTTPBearer(auto_error=False)

def get_token_from_header(auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    if auth_header and auth_header.credentials:
        return auth_header.credentials.strip()
    return None

def get_current_user(
    token: Optional[str] = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    if not token:
        raise HTTPException(status_code=401, detail="Authentication token required. Please sign in.")
    user = auth_service.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please sign in again.")
    return user

def get_optional_user(
    token: Optional[str] = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    return auth_service.get_user_by_token(token)

# ------------------------------------------------------------------------------
# Authentication Endpoints
# ------------------------------------------------------------------------------
@router.post("/auth/register", response_model=AuthResponse)
def register(request: UserRegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        res = auth_service.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return AuthResponse(
            user=UserProfile(**res["user"]),
            token=res["token"],
            message=f"Welcome to JurisAI, {res['user']['username']}!"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.post("/auth/login", response_model=AuthResponse)
def login(request: UserLoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        res = auth_service.authenticate_user(
            username_or_email=request.username_or_email,
            password=request.password
        )
        return AuthResponse(
            user=UserProfile(**res["user"]),
            token=res["token"],
            message=f"Welcome back, {res['user']['username']}!"
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.post("/auth/logout")
def logout(
    token: Optional[str] = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service)
):
    if token:
        auth_service.revoke_token(token)
    return {"message": "Logged out successfully."}

@router.get("/auth/me", response_model=UserProfile)
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return UserProfile(**user)

# ------------------------------------------------------------------------------
# Search & Case Analysis History Endpoints
# ------------------------------------------------------------------------------
@router.get("/history", response_model=List[HistoryItemSummary])
def get_history(
    limit: int = 50,
    user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Retrieve chronologically ordered search & analysis history for the current user."""
    items = auth_service.get_user_history(user_id=user["id"], limit=limit)
    return [HistoryItemSummary(**i) for i in items]

@router.get("/history/{history_id}", response_model=HistoryDetailResponse)
def get_history_detail(
    history_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Retrieve full analysis data for a past case to restore state in the workspace."""
    item = auth_service.get_history_item(user_id=user["id"], history_id=history_id)
    if not item:
        raise HTTPException(status_code=404, detail="History record not found.")
    return HistoryDetailResponse(**item)

@router.post("/history", response_model=Dict[str, Any])
def add_history_entry(
    entry: SaveHistoryRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Manually record a search query or analysis in user's history."""
    analysis_json = json.dumps(entry.analysis_data) if entry.analysis_data else None
    history_id = auth_service.save_history(
        user_id=user["id"],
        query_text=entry.query_text,
        case_type=entry.case_type,
        outcome=entry.outcome,
        summary=entry.summary,
        analysis_id=entry.analysis_id,
        analysis_data_json=analysis_json
    )
    return {"id": history_id, "message": "History saved successfully."}

@router.delete("/history/{history_id}")
def delete_history_entry(
    history_id: int,
    user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Remove a specific analysis from user's history."""
    deleted = auth_service.delete_history_item(user_id=user["id"], history_id=history_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History record not found.")
    return {"message": "History entry deleted successfully."}

@router.delete("/history")
def clear_history(
    user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Clear all past search and analysis history for the current user."""
    count = auth_service.clear_user_history(user_id=user["id"])
    return {"message": f"Cleared {count} history entries."}

