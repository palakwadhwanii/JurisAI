import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from reanalysis_system import Phase15WorkflowOrchestrator, WorkflowOutcome
from vector_query_service import LegalVectorStore

class JurisAIEngine:
    """
    Core backend service bridging FastAPI endpoints to the 8-agent self-checking system.
    Built for Indian Family Law constraint-aware analysis.
    """
    def __init__(self):
        print("[JurisAIEngine] Bootstrapping multi-agent orchestrator and vector store...")
        self.orchestrator = Phase15WorkflowOrchestrator()
        self.vector_store = self.orchestrator.vector_store

    def analyze_case(self, case_text: str, uploaded_docs: Optional[List[str]] = None, inject_fault: Optional[str] = None, analysis_id: Optional[str] = None) -> Dict[str, Any]:
        import uuid
        active_analysis_id = analysis_id or f"analysis-{uuid.uuid4().hex[:12]}"
        
        combined_text = case_text.strip()
        if uploaded_docs:
            docs_block = "\n\n=== ATTACHED EVIDENCE / DOCUMENTS ===\n" + "\n".join(uploaded_docs)
            combined_text += docs_block

        # Run Phase 15 self-checking orchestrator with unique analysis_id
        res = self.orchestrator.run(combined_text, inject_test_fault=inject_fault, analysis_id=active_analysis_id)

        # Package full agent traces for the inspection dashboard
        latest_audit = res["audit_history"][-1] if res["audit_history"] else {}
        
        return {
            "analysis_id": active_analysis_id,
            "case_state": res.get("case_state", {}),
            "outcome": res["outcome"],
            "total_iterations": res["total_iterations"],
            "audit_history": res["audit_history"],
            "agent_outputs": {
                "law_sections": res.get("law_output", {}).get("sections", []),
                "precedents": res.get("precedent_output", {}).get("cases", []),
                "evidence_support": res.get("evidence_output", {}).get("evidence_support", []),
                "evidence_gaps": res.get("evidence_output", {}).get("evidence_gaps", []),
                "procedural_constraints": res.get("constraint_output", {}).get("procedural_constraints", []),
                "substantive_constraints": res.get("constraint_output", {}).get("substantive_constraints", []),
                "opposition_objections": res.get("opposition_output", {}).get("objections", []),
                "opposition_counterarguments": res.get("opposition_output", {}).get("counterarguments", [])
            },
            "final_judgment": res["final_report"],
            "elapsed_seconds": res["elapsed_seconds"]
        }

    def parse_document(self, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        """
        Parses text or PDF files. Uses pymupdf if available, else utf-8 decode.
        """
        extracted = ""
        fn_lower = filename.lower()
        if fn_lower.endswith(".pdf"):
            try:
                import fitz
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                pages = [page.get_text() for page in doc]
                extracted = "\n".join(pages)
            except Exception as e:
                extracted = f"Error extracting PDF text: {str(e)}"
        else:
            try:
                extracted = content_bytes.decode("utf-8", errors="ignore")
            except Exception:
                extracted = str(content_bytes)

        # Detect legal entities from document
        detected_entities = []
        if "settlement" in extracted.lower():
            detected_entities.append("Memorandum of Settlement / Consent Terms")
        if "affidavit" in extracted.lower():
            detected_entities.append("Sworn Affidavit / Financial Disclosure")
        if "13b" in extracted.lower():
            detected_entities.append("Mutual Consent Petition Under Section 13B")
        if "fir" in extracted.lower() or "498a" in extracted.lower():
            detected_entities.append("Criminal Complaint / Section 498A IPC")

        return {
            "filename": filename,
            "extracted_text": extracted.strip(),
            "char_count": len(extracted),
            "detected_entities": detected_entities
        }

    def get_sample_cases(self) -> List[Dict[str, Any]]:
        """
        Curated benchmark cases representing Indian Family Law disputes.
        """
        return [
            {
                "id": "case-01-mutual-consent-waiver",
                "title": "Mutual Consent Divorce & 6-Month Cooling-Off Waiver",
                "category": "Hindu Marriage Act, 1955",
                "facts_summary": "Parties married in 2020, separated for over 2 years, settled all alimony and custody, seeking immediate waiver under Section 13B(2).",
                "full_text": (
                    "I got married in 2020 under the Hindu Marriage Act. My husband and I have been living separately "
                    "for over 2 years due to severe compatibility issues. We have now reached a comprehensive settlement agreement "
                    "and wish to dissolve our marriage by mutual consent under Section 13B. We want to know if the 6-month cooling-off "
                    "period can be waived and how permanent alimony will be finalized by the court."
                ),
                "engineering_notes": "Tests Constraint Hunter for Section 13B(2) temporal limitation and checks Precedent Agent for Shilpa Sailesh (2023 INSC 468) and Amardeep Singh waiver doctrine."
            },
            {
                "id": "case-02-mental-cruelty-false-fir",
                "title": "Contested Divorce on Mental Cruelty & False FIRs",
                "category": "Hindu Marriage Act, 1955 (Section 13(1)(ia))",
                "facts_summary": "Husband filed divorce alleging mental cruelty after wife filed multiple false criminal complaints under 498A that resulted in acquittal.",
                "full_text": (
                    "Marriage solemnized in 2018 under Hindu rites. After continuous discord, wife left matrimonial home in 2021 "
                    "and lodged criminal complaints under Section 498A IPC and Section 125 CrPC against husband and elderly parents. "
                    "The criminal trial ended in complete acquittal, with the magistrate observing false allegations. "
                    "Husband now claims dissolution of marriage on grounds of mental cruelty under Section 13(1)(ia)."
                ),
                "engineering_notes": "Tests Evidence Agent on criminal acquittal records and tests Opposition Agent on whether matrimonial friction meets mental cruelty thresholds."
            },
            {
                "id": "case-03-pwdva-shared-household",
                "title": "Domestic Violence Residence Order & Shared Household",
                "category": "Protection of Women from Domestic Violence Act, 2005",
                "facts_summary": "Wife seeking right of residence in shared household owned by father-in-law under Sections 17 and 19 of PWDVA.",
                "full_text": (
                    "Applicant married respondent in 2019 and resided in a joint family house standing in the name of the father-in-law. "
                    "Following severe marital discord, applicant was dispossessed from the house. "
                    "Applicant seeks protection orders and right of residence in the shared household under Section 17 and Section 19 of PWDVA 2005."
                ),
                "engineering_notes": "Tests Law Agent on PWDVA Sections 17 and 19, and verifies Precedent Agent on Satish Chander Ahuja v. Sneha Ahuja Supreme Court doctrine."
            }
        ]

import threading

# Global thread-safe singleton instance
engine_instance = None
_engine_lock = threading.Lock()

def get_engine() -> JurisAIEngine:
    global engine_instance
    if engine_instance is None:
        with _engine_lock:
            if engine_instance is None:
                engine_instance = JurisAIEngine()
    return engine_instance
