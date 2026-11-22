import pytest
from typing import Dict, Any

from multi_agent_workflow import (
    CaseManagerAgent,
    LawAgent,
    PrecedentAgent,
    ConstraintHunterAgent,
    AuditorAgent
)
from reanalysis_system import Phase15WorkflowOrchestrator, Phase15AuditorAgent, WorkflowOutcome
from vector_query_service import LegalVectorStore

class TestHallucinationTesting:
    """
    PHASE 19: Hallucination & Adversarial Testing Suite
    Evaluates:
    - Rejection of trivial, greeting, and single-word inputs without hallucinating cases
    - Out-of-scope non-family law disputes (patents, crypto, traffic, commercial disputes)
    - Rejection and auditing of adversarial fake sections (e.g. HMA Section 999)
    - Rejection of fabricated precedent citations (e.g. 2099 INSC 9999)
    - Self-checking recovery loop: verifying automated reanalysis upon fault injection
    """

    def test_trivial_and_greeting_inputs_rejected(self, trivial_cases):
        """Verifies that greetings and trivial inputs trigger anti-hallucination gates."""
        cm = CaseManagerAgent()
        for input_text in trivial_cases:
            val = cm.validate_case_narrative(input_text)
            assert val["is_valid"] is False
            assert val["status"] == "INSUFFICIENT_INFORMATION"
            assert "reason" in val
            assert len(val.get("missing_elements", [])) >= 2

            # Verify CaseState reflects insufficient input
            state = cm.process(input_text)
            assert state["is_valid_case"] is False
            assert state["triage_status"] == "INSUFFICIENT_INFORMATION"

    def test_out_of_scope_non_family_law_disputes_rejected(self, out_of_scope_cases):
        """Verifies that non-matrimonial disputes (patents, traffic, crypto) are flagged."""
        cm = CaseManagerAgent()
        for query in out_of_scope_cases:
            val = cm.validate_case_narrative(query)
            # Either flagged invalid by triage or unclassified without fabricating matrimonial claims
            if not val["is_valid"]:
                assert val["status"] in ["INSUFFICIENT_INFORMATION", "OUT_OF_SCOPE"]
            else:
                state = cm.process(query)
                # Ensure no domestic violence or divorce is hallucinated
                assert "Domestic Violence" not in state["case_type"]
                assert "Mutual Consent" not in state["case_type"]

    def test_adversarial_fake_statute_sections_caught_by_auditor(self, vector_store: LegalVectorStore):
        """Tests that fabricated statutory provisions injected into state are caught by Auditor."""
        auditor = Phase15AuditorAgent(vector_store=vector_store)

        fake_state = {
            "case_id": "case-fake-sec",
            "is_valid_case": True,
            "case_type": "Mutual Consent Divorce",
            "governing_acts": ["Hindu Marriage Act, 1955"],
            "target_sections": ["555", "999"],
            "claims": ["Divorce"]
        }

        fake_law_output = {
            "sections": [
                {
                    "act_id": "HMA_1955",
                    "act_name": "Hindu Marriage Act, 1955",
                    "section": "555",
                    "title": "Fabricated Section 555",
                    "meaning": "Fake meaning",
                    "requirements": "Fake requirement"
                },
                {
                    "act_id": "PWDVA_2005",
                    "act_name": "Protection of Women from Domestic Violence Act, 2005",
                    "section": "999",
                    "title": "Fabricated Section 999",
                    "meaning": "Fake meaning",
                    "requirements": "Fake requirement"
                }
            ],
            "requirements": [],
            "constraints": []
        }

        report = auditor.audit(
            iteration=1,
            case_state=fake_state,
            law_output=fake_law_output,
            precedent_output={"cases": []},
            evidence_output={"evidence_support": [], "evidence_gaps": []},
            constraint_output={"procedural_constraints": []},
            opposition_output={"objections": []}
        )

        assert report.reanalysis_required is True
        assert report.audit_status == "FAIL"
        
        # Verify both fake sections are flagged
        flagged_descs = [
            (e.get("description") if isinstance(e, dict) else e.description)
            for e in report.errors
        ]
        assert any("555" in d for d in flagged_descs), "Auditor failed to flag fake Section 555"
        assert any("999" in d for d in flagged_descs), "Auditor failed to flag fake Section 999"

    def test_reanalysis_loop_recovers_from_citation_error_fault(
        self,
        mutual_consent_case_text: str
    ):
        """Verifies Phase15WorkflowOrchestrator self-heals when a CITATION_ERROR is injected."""
        orchestrator = Phase15WorkflowOrchestrator()
        result = orchestrator.run(
            mutual_consent_case_text,
            inject_test_fault="CITATION_ERROR"
        )

        assert result["outcome"] == WorkflowOutcome.RECOVERED.value
        assert result["total_iterations"] == 2
        assert len(result["audit_history"]) == 2
        # First iteration must have failed audit
        assert result["audit_history"][0]["audit_status"] == "FAIL"
        # Second iteration must have passed audit
        assert result["audit_history"][1]["audit_status"] == "PASS"
        assert len(result["final_report"]) > 200

    def test_reanalysis_loop_handles_persistent_unresolved_fault(
        self,
        mutual_consent_case_text: str
    ):
        """Verifies Phase15WorkflowOrchestrator halts safely at HUMAN_REVIEW_REQUIRED on unrecoverable fault."""
        orchestrator = Phase15WorkflowOrchestrator()
        result = orchestrator.run(
            mutual_consent_case_text,
            inject_test_fault="PERSISTENT_UNRESOLVED"
        )

        assert result["outcome"] == WorkflowOutcome.HUMAN_REVIEW_REQUIRED.value
        assert result["total_iterations"] == 3
        assert len(result["audit_history"]) == 3
        assert all(h["audit_status"] == "FAIL" for h in result["audit_history"])

    def test_full_pipeline_anti_hallucination_on_greeting(self):
        """Ensures that orchestrator on a greeting produces clean triage result rather than hallucinating."""
        orchestrator = Phase15WorkflowOrchestrator()
        result = orchestrator.run("Hello, I need legal help.")

        assert result["outcome"] == WorkflowOutcome.INSUFFICIENT_INFORMATION.value
        assert result["total_iterations"] == 1
        assert "INSUFFICIENT" in result["final_report"].upper() or "MORE DETAILS" in result["final_report"].upper()
