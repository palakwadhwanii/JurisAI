import pytest
from typing import Dict, Any

from multi_agent_workflow import (
    CaseManagerAgent,
    LawAgent,
    PrecedentAgent,
    EvidenceAgent,
    ConstraintHunterAgent,
    OppositionAgent,
    AuditorAgent,
    JudgeAgent
)
from vector_query_service import LegalVectorStore

class TestAgentEvaluation:
    """
    PHASE 19: Agent Evaluation Suite
    Evaluates each of the 8 agents in isolation and in sequenced state transitions:
    1. CaseManagerAgent (Triage, entity extraction, narrative validation)
    2. LawAgent (Statute mapping, requirements, provisos)
    3. PrecedentAgent (Ratio decidendi, Supreme Court citations, relevance tiers)
    4. EvidenceAgent (Proof standards, evidentiary gap analysis)
    5. ConstraintHunterAgent (Procedural bars, cooling-off periods, statutory limits)
    6. OppositionAgent (Adversarial counsel objections & counterclaims)
    7. AuditorAgent (Citation validation, contamination checking, audit status)
    8. JudgeAgent (12-part synthesis, judicial decree outlook)
    """

    def test_case_manager_agent_validation_and_parsing(self, mutual_consent_case_text: str):
        """Tests CaseManagerAgent extracts entities, dates, acts, sections, and issues."""
        agent = CaseManagerAgent()
        
        # 1. Test validation on valid case
        val = agent.validate_case_narrative(mutual_consent_case_text)
        assert val["is_valid"] is True

        # 2. Test processing into CaseState
        state = agent.process(mutual_consent_case_text)
        assert state["is_valid_case"] is True
        assert state["case_id"] is not None
        assert any("Hindu Marriage" in a or "HMA" in a for a in state["governing_acts"])
        assert any("13B" in str(s).upper() for s in state["target_sections"])
        assert len(state["facts"]) >= 1
        assert len(state["legal_issues"]) >= 1

    def test_case_manager_agent_rejects_insufficient_input(self, trivial_cases):
        """Tests CaseManagerAgent gates against insufficient, vague, or greeting inputs."""
        agent = CaseManagerAgent()
        for trivial in trivial_cases:
            val = agent.validate_case_narrative(trivial)
            assert val["is_valid"] is False
            assert val["status"] == "INSUFFICIENT_INFORMATION"
            assert len(val["missing_elements"]) > 0

            # State processing must reflect invalid state
            state = agent.process(trivial)
            assert state["is_valid_case"] is False
            assert state["triage_status"] == "INSUFFICIENT_INFORMATION"

    def test_law_agent_retrieval_and_provisos(self, vector_store: LegalVectorStore, mutual_consent_case_text: str):
        """Tests LawAgent retrieves statutory sections, requirements, and provisos."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)
        
        law_agent = LawAgent(vector_store=vector_store)
        law_out = law_agent.process(state)

        assert "sections" in law_out
        sections = law_out["sections"]
        assert len(sections) > 0

        # Verify Section 13B is present
        sec_numbers = [str(s.get("section", "")).upper() for s in sections]
        assert any("13B" in sn for sn in sec_numbers), f"Expected 13B in retrieved sections: {sec_numbers}"

        # Verify section content structure
        target_s = next(s for s in sections if "13B" in str(s.get("section", "")).upper())
        assert len(target_s.get("title", "")) > 0
        assert len(target_s.get("meaning", "")) > 0
        assert len(target_s.get("requirements", "")) > 0

    def test_precedent_agent_ratios_and_citations(self, vector_store: LegalVectorStore, mutual_consent_case_text: str):
        """Tests PrecedentAgent retrieves binding Supreme Court citations and ratios."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)

        prec_agent = PrecedentAgent(vector_store=vector_store)
        prec_out = prec_agent.process(state)

        assert "cases" in prec_out
        cases = prec_out["cases"]
        assert len(cases) > 0

        # Precedents must have case name, citations, and ratio
        for c in cases:
            assert len(c["case_name"]) > 0
            assert len(c.get("scr_citation", "")) > 0 or len(c.get("insc_citation", "")) > 0
            assert len(c.get("ratio", "")) > 0
            assert c.get("relevance_tier") in ["DIRECT", "RELATED", "SUPPORTING", "PERSUASIVE"]

    def test_evidence_agent_gap_analysis(self, vector_store: LegalVectorStore, cruelty_divorce_case_text: str):
        """Tests EvidenceAgent evaluates evidentiary requirements, support, and gaps."""
        cm = CaseManagerAgent()
        state = cm.process(cruelty_divorce_case_text)

        law_out = LawAgent(vector_store=vector_store).process(state)
        ev_agent = EvidenceAgent()
        ev_out = ev_agent.process(state, law_out)

        assert "evidence_support" in ev_out
        assert "evidence_gaps" in ev_out
        assert "weaknesses" in ev_out

        # In a 498A acquittal case, certified copy of judgment should be flagged
        assert len(ev_out["evidence_support"]) > 0 or len(ev_out["evidence_gaps"]) > 0

    def test_constraint_hunter_agent_procedural_bars(
        self,
        vector_store: LegalVectorStore,
        mutual_consent_case_text: str
    ):
        """Tests ConstraintHunterAgent uncovers statutory cooling-off periods and bars."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)

        law_out = LawAgent(vector_store=vector_store).process(state)
        prec_out = PrecedentAgent(vector_store=vector_store).process(state)
        ev_out = EvidenceAgent().process(state, law_out)

        ch_agent = ConstraintHunterAgent()
        ch_out = ch_agent.process(state, law_out, prec_out, ev_out)

        assert "procedural_constraints" in ch_out
        constraints = ch_out["procedural_constraints"]
        assert len(constraints) > 0

        # Check for 6-month statutory waiting / cooling-off constraint
        cooling_off_flagged = any(
            "cooling" in str(c).lower() or "6 month" in str(c).lower() or "13b" in str(c).lower() or "reflection" in str(c).lower()
            for c in constraints
        )
        assert cooling_off_flagged, f"Section 13B(2) cooling-off period not flagged in constraints: {constraints}"

    def test_opposition_agent_adversarial_counterclaims(
        self,
        vector_store: LegalVectorStore,
        mutual_consent_case_text: str
    ):
        """Tests OppositionAgent formulates defense objections and adversarial counsel arguments."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)

        law_out = LawAgent(vector_store=vector_store).process(state)
        prec_out = PrecedentAgent(vector_store=vector_store).process(state)
        ev_out = EvidenceAgent().process(state, law_out)
        ch_out = ConstraintHunterAgent().process(state, law_out, prec_out, ev_out)

        opp_agent = OppositionAgent()
        opp_out = opp_agent.process(state, law_out, ev_out, ch_out)

        assert "objections" in opp_out
        assert "counterarguments" in opp_out
        assert len(opp_out["objections"]) > 0 or len(opp_out["counterarguments"]) > 0

    def test_auditor_agent_verifies_consistent_workflow(
        self,
        vector_store: LegalVectorStore,
        mutual_consent_case_text: str
    ):
        """Tests AuditorAgent cross-checks citations and flags valid workflows as PASS/WARN."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)
        
        law_out = LawAgent(vector_store=vector_store).process(state)
        prec_out = PrecedentAgent(vector_store=vector_store).process(state)
        ev_out = EvidenceAgent().process(state, law_out)
        ch_out = ConstraintHunterAgent().process(state, law_out, prec_out, ev_out)

        auditor = AuditorAgent()
        audit_res = auditor.process(state, law_out, prec_out, ch_out)

        assert audit_res["audit_status"] in ["PASS", "WARN"]
        assert audit_res["reanalysis_required"] is False
        assert len(audit_res["citation_validation"]) > 0
        assert all(c.get("valid") is True for c in audit_res["citation_validation"])

    def test_judge_agent_structured_assessment(
        self,
        vector_store: LegalVectorStore,
        mutual_consent_case_text: str
    ):
        """Tests JudgeAgent synthesizes the complete multi-agent findings into a final judicial assessment."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)
        
        law_out = LawAgent(vector_store=vector_store).process(state)
        prec_out = PrecedentAgent(vector_store=vector_store).process(state)
        ev_out = EvidenceAgent().process(state, law_out)
        ch_out = ConstraintHunterAgent().process(state, law_out, prec_out, ev_out)
        opp_out = OppositionAgent().process(state, law_out, ev_out, ch_out)

        auditor = AuditorAgent()
        audit_res = auditor.process(state, law_out, prec_out, ch_out)

        judge = JudgeAgent()
        judgment = judge.process(state, law_out, prec_out, ev_out, ch_out, opp_out, audit_res)

        assert isinstance(judgment, str)
        assert len(judgment) > 300
        # Check judicial assessment sections
        assert "STATUTORY" in judgment.upper() or "LEGAL" in judgment.upper() or "ACT" in judgment.upper()
        assert "EVIDENCE" in judgment.upper() or "PROCEDURAL" in judgment.upper() or "COURT" in judgment.upper()
        assert "DECREE" in judgment.upper() or "OUTLOOK" in judgment.upper() or "PROBABLE" in judgment.upper() or "ASSESSMENT" in judgment.upper()
