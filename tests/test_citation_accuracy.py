import re
import pytest
from typing import Dict, Any, List

from multi_agent_workflow import (
    CaseManagerAgent,
    LawAgent,
    PrecedentAgent,
    ConstraintHunterAgent,
    EvidenceAgent,
    AuditorAgent
)
from reanalysis_system import Phase15AuditorAgent, ErrorType
from vector_query_service import LegalVectorStore

class TestCitationAccuracy:
    """
    PHASE 19: Citation Accuracy Evaluation Suite
    Evaluates:
    - Ground-truth validity of statutory citations against section_metadata.json
    - Ground-truth validity of Supreme Court precedents against verified database
    - Formatting compliance of official SCR, SCC, and INSC citation patterns
    - Detection of corrupted, non-existent, or hallucinated citations by the Auditor Agent
    - Precision, Recall, and False Citation Rate metrics
    """

    def test_statutory_citations_exist_in_official_index(
        self,
        vector_store: LegalVectorStore,
        section_metadata: Dict[str, Any],
        mutual_consent_case_text: str,
        pwdva_case_text: str,
        cruelty_divorce_case_text: str
    ):
        """Verifies all statutory citations produced by LawAgent map to real sections in section_metadata.json."""
        # Build ground-truth lookup: {act_name_lower: set_of_section_numbers}
        valid_sections = {}
        for act in section_metadata.get("acts", []):
            name_lower = act["act_name"].lower()
            id_lower = act["act_id"].lower()
            secs = {str(s["section_number"]).lower().strip() for s in act.get("sections", [])}
            valid_sections[name_lower] = secs
            valid_sections[id_lower] = secs

        cm = CaseManagerAgent()
        law_agent = LawAgent(vector_store=vector_store)

        for case_text in [mutual_consent_case_text, pwdva_case_text, cruelty_divorce_case_text]:
            state = cm.process(case_text)
            law_out = law_agent.process(state)

            sections = law_out.get("sections", [])
            assert len(sections) > 0, "No sections retrieved by LawAgent"

            for s in sections:
                act_name = s.get("act_name", "").lower()
                act_id = s.get("act_id", "").lower()
                sec_num = str(s.get("section", "")).lower().strip()

                # Extract base section number (e.g. '13(1)(ia)' -> '13', '13B' -> '13b')
                match = re.match(r"^(\d+[a-zA-Z]?)", sec_num)
                assert match is not None, f"Could not parse section number from: {sec_num}"
                base_sec = match.group(1).lower()

                matched_act_secs = valid_sections.get(act_name) or valid_sections.get(act_id)
                assert matched_act_secs is not None, f"Act '{s.get('act_name')}' not found in official statutory index"
                assert base_sec in matched_act_secs, (
                    f"Base Section '{base_sec}' (from '{sec_num}') of '{s.get('act_name')}' is not in statutory corpus"
                )

    def test_precedent_citations_exist_in_judgment_metadata(
        self,
        vector_store: LegalVectorStore,
        judgment_metadata: List[Dict[str, Any]],
        mutual_consent_case_text: str,
        cruelty_divorce_case_text: str
    ):
        """Verifies Supreme Court citations retrieved by PrecedentAgent correspond to verified judgments."""
        valid_insc_set = {j.get("insc_citation", "").strip() for j in judgment_metadata if j.get("insc_citation")}
        valid_names_lower = {j.get("case_name", "").lower().strip() for j in judgment_metadata if j.get("case_name")}

        cm = CaseManagerAgent()
        prec_agent = PrecedentAgent(vector_store=vector_store)

        for case_text in [mutual_consent_case_text, cruelty_divorce_case_text]:
            state = cm.process(case_text)
            prec_out = prec_agent.process(state)

            cases = prec_out.get("cases", [])
            assert len(cases) > 0, "No precedents retrieved by PrecedentAgent"

            for c in cases:
                insc = c.get("insc_citation", "").strip()
                name = c.get("case_name", "").lower().strip()
                
                # Must either be directly in judgment_metadata or have a valid Supreme Court INSC identifier
                is_in_metadata = (insc in valid_insc_set) or any(n in name or name in n for n in valid_names_lower)
                has_valid_sc_pattern = bool(re.search(r"\d{4}\s+INSC\s+\d+", insc)) or bool(re.search(r"\d{4}\s+SCC", c.get("scr_citation", "")))

                assert is_in_metadata or has_valid_sc_pattern, (
                    f"Retrieved precedent '{c.get('case_name')}' ({c.get('scr_citation')} | {insc}) is unverified"
                )

    def test_scr_and_insc_citation_format_compliance(
        self,
        vector_store: LegalVectorStore,
        mutual_consent_case_text: str
    ):
        """Verifies all precedent citations adhere strictly to official SCR, SCC, or INSC syntax."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)
        prec_out = PrecedentAgent(vector_store=vector_store).process(state)

        # INSC format: e.g. '2023 INSC 468' or '2024 INSC 123'
        insc_pattern = re.compile(r"^\d{4}\s+INSC\s+\d+$", re.IGNORECASE)
        # SCR or SCC reporter format
        reporter_pattern = re.compile(r"(\[\d{4}\]\s+\d+\s+S\.C\.R\.\s+\d+|\(\d{4}\)\s+\d+\s+SCC\s+\d+|AIR\s+\d{4}\s+SC)", re.IGNORECASE)

        for c in prec_out.get("cases", []):
            insc = c.get("insc_citation", "").strip()
            scr = c.get("scr_citation", "").strip()

            if insc:
                assert insc_pattern.match(insc), f"Invalid INSC citation format: '{insc}'"
            if scr:
                assert reporter_pattern.search(scr), f"Invalid SCR/SCC citation format: '{scr}'"

    def test_auditor_detects_hallucinated_statutory_sections(self, vector_store: LegalVectorStore):
        """Tests that Phase15AuditorAgent flags non-existent sections with CITATION_ERROR."""
        auditor = Phase15AuditorAgent(vector_store=vector_store)

        mock_case_state = {
            "case_id": "test-audit-hallucination",
            "is_valid_case": True,
            "case_type": "Mutual Consent Divorce",
            "governing_acts": ["Hindu Marriage Act, 1955"],
            "target_sections": ["999"],
            "claims": ["Divorce"]
        }
        # Injected fake section
        corrupted_law_output = {
            "sections": [
                {
                    "act_id": "HMA_1955",
                    "act_name": "Hindu Marriage Act, 1955",
                    "section": "999",  # Completely fabricated section
                    "title": "Non-existent fantasy section",
                    "meaning": "Fabricated text",
                    "requirements": "Fake requirement"
                }
            ],
            "requirements": [],
            "constraints": []
        }

        mock_precedents = {"cases": []}
        mock_evidence = {"evidence_support": [], "evidence_gaps": []}
        mock_constraints = {"procedural_constraints": []}
        mock_opposition = {"objections": []}

        report = auditor.audit(
            iteration=1,
            case_state=mock_case_state,
            law_output=corrupted_law_output,
            precedent_output=mock_precedents,
            evidence_output=mock_evidence,
            constraint_output=mock_constraints,
            opposition_output=mock_opposition
        )

        # Auditor must flag error
        assert report.reanalysis_required is True
        assert len(report.errors) > 0
        citation_errors = [e for e in report.errors if (e.get("type") if isinstance(e, dict) else e.type) == ErrorType.CITATION_ERROR.value]
        assert len(citation_errors) > 0, "Auditor failed to flag non-existent Section 999 as CITATION_ERROR"
        desc = citation_errors[0].get("description") if isinstance(citation_errors[0], dict) else citation_errors[0].description
        assert "999" in desc

    def test_citation_precision_score_on_grounded_pipeline(
        self,
        vector_store: LegalVectorStore,
        mutual_consent_case_text: str
    ):
        """Measures citation precision: (verified citations / total citations) must equal 1.0 (100%)."""
        cm = CaseManagerAgent()
        state = cm.process(mutual_consent_case_text)
        
        law_out = LawAgent(vector_store=vector_store).process(state)
        prec_out = PrecedentAgent(vector_store=vector_store).process(state)
        ev_out = EvidenceAgent().process(state, law_out)
        ch_out = ConstraintHunterAgent().process(state, law_out, prec_out, ev_out)

        auditor = AuditorAgent()
        audit_res = auditor.process(state, law_out, prec_out, ch_out)

        verifications = audit_res.get("citation_validation", [])
        assert len(verifications) > 0, "No citations verified"

        valid_count = sum(1 for c in verifications if c.get("valid") is True)
        total_count = len(verifications)
        precision = valid_count / total_count

        assert precision == 1.0, f"Citation precision fell below 100%: got {precision * 100:.1f}%"
