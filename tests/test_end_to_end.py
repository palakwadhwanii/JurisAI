import io
import time
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.schemas import CaseAnalysisResponse, DocumentUploadResponse
from multi_agent_workflow import MultiAgentLegalSystem
from reanalysis_system import Phase15WorkflowOrchestrator
from vector_query_service import LegalVectorStore

class TestEndToEnd:
    """
    PHASE 19: End-to-End Testing Suite
    Evaluates:
    - Complete multi-agent pipeline execution across core Indian Family Law scenarios
    - FastAPI REST API endpoints:
        * GET /api/health
        * GET /api/sample-cases
        * POST /api/analyze
        * POST /api/upload-document
        * GET /metrics (Prometheus telemetry)
    - Full schema conformance and response timing
    """

    def test_e2e_multi_agent_system_mutual_consent(
        self,
        multi_agent_system: MultiAgentLegalSystem,
        mutual_consent_case_text: str
    ):
        """End-to-end execution of MultiAgentLegalSystem on Mutual Consent Divorce."""
        t_start = time.perf_counter()
        result = multi_agent_system.run(mutual_consent_case_text)
        duration = time.perf_counter() - t_start

        assert "case_state" in result
        assert "law_output" in result
        assert "precedent_output" in result
        assert "evidence_output" in result
        assert "constraint_output" in result
        assert "opposition_output" in result
        assert "final_judgment" in result
        assert "auditor_output" in result

        assert result["case_state"]["is_valid_case"] is True
        assert len(result["law_output"]["sections"]) > 0
        assert len(result["precedent_output"]["cases"]) > 0
        assert len(result["final_judgment"]) > 300
        assert duration < 5.0, f"Analysis took too long: {duration:.2f}s"

    def test_e2e_multi_agent_system_pwdva_shared_household(
        self,
        multi_agent_system: MultiAgentLegalSystem,
        pwdva_case_text: str
    ):
        """End-to-end execution on Domestic Violence & Shared Household claim."""
        result = multi_agent_system.run(pwdva_case_text)

        assert result["case_state"]["is_valid_case"] is True
        # Check that PWDVA Sections 17 or 19 are cited
        sec_nums = [str(s.get("section", "")) for s in result["law_output"]["sections"]]
        assert any("17" in sn or "19" in sn for sn in sec_nums), f"Expected Sec 17/19 in: {sec_nums}"
        assert len(result["final_judgment"]) > 200

    def test_api_health_endpoint(self, api_client: TestClient):
        """Tests GET /api/health responds with healthy status and collection stats."""
        res = api_client.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["acts_covered"] == 12
        assert data["precedents_indexed"] == 91
        assert data["chroma_master_chunks"] == 916
        assert len(data["agents_available"]) == 8

    def test_api_sample_cases_endpoint(self, api_client: TestClient):
        """Tests GET /api/sample-cases returns curated benchmark cases."""
        res = api_client.get("/api/sample-cases")
        assert res.status_code == 200
        cases = res.json()
        assert isinstance(cases, list)
        assert len(cases) >= 3
        for c in cases:
            assert "id" in c
            assert "title" in c
            assert "full_text" in c
            assert len(c["full_text"]) > 50

    def test_api_analyze_case_endpoint(
        self,
        api_client: TestClient,
        mutual_consent_case_text: str
    ):
        """Tests POST /api/analyze conforms strictly to CaseAnalysisResponse schema."""
        payload = {
            "case_text": mutual_consent_case_text,
            "uploaded_documents": [],
            "sub_case_type": "Mutual Consent Divorce"
        }
        res = api_client.post("/api/analyze", json=payload)
        assert res.status_code == 200
        data = res.json()

        # Validate with Pydantic model
        validated = CaseAnalysisResponse(**data)
        assert validated.outcome in ["PASS", "RECOVERED"]
        assert validated.total_iterations >= 1
        assert len(validated.final_judgment) > 200
        assert validated.elapsed_seconds > 0.0

        # Check agent outputs in response
        outputs = data.get("agent_outputs", {})
        assert len(outputs.get("law_sections", [])) > 0
        assert len(outputs.get("precedents", [])) > 0
        assert len(outputs.get("procedural_constraints", [])) > 0

    def test_api_upload_document_text_file(self, api_client: TestClient):
        """Tests POST /api/upload-document with text content."""
        doc_content = (
            "MEMORANDUM OF SETTLEMENT AND CONCENT TERMS\n"
            "Both parties mutually agree to dissolve marriage under Section 13B of Hindu Marriage Act.\n"
            "Full and final permanent alimony of Rs 25,00,000 paid via Demand Draft."
        )
        file_obj = io.BytesIO(doc_content.encode("utf-8"))
        res = api_client.post(
            "/api/upload-document",
            files={"file": ("settlement_agreement.txt", file_obj, "text/plain")}
        )
        assert res.status_code == 200
        data = res.json()
        validated = DocumentUploadResponse(**data)
        assert validated.filename == "settlement_agreement.txt"
        assert validated.char_count > 50
        assert "13b" in validated.extracted_text.lower()
        assert any("Settlement" in e or "13B" in e for e in validated.detected_entities)

    def test_prometheus_metrics_endpoint(self, api_client: TestClient):
        """Tests GET /metrics exposes Prometheus telemetry metrics."""
        res = api_client.get("/metrics")
        assert res.status_code == 200
        content = res.text
        assert "jurisai_api_requests_total" in content
        assert "jurisai_case_analyses_total" in content
        assert "jurisai_rag_retrieval_duration_seconds" in content
