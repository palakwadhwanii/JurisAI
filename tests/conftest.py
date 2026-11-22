import os
import sys
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vector_query_service import LegalVectorStore
from legal_rag_pipeline import QueryProcessor, HybridRetriever, RerankerFilter, ContextBuilder
from multi_agent_workflow import (
    MultiAgentLegalSystem,
    CaseManagerAgent,
    LawAgent,
    PrecedentAgent,
    EvidenceAgent,
    ConstraintHunterAgent,
    OppositionAgent,
    AuditorAgent,
    JudgeAgent
)
from reanalysis_system import Phase15AuditorAgent, Phase15WorkflowOrchestrator
from backend.main import app
from backend.services.jurisai_engine import get_engine, JurisAIEngine

@pytest.fixture(scope="session")
def vector_store():
    """Session-scoped vector store instance (pre-indexed 916 chunks)."""
    return LegalVectorStore()

@pytest.fixture(scope="session")
def query_processor():
    return QueryProcessor()

@pytest.fixture(scope="session")
def hybrid_retriever(vector_store):
    return HybridRetriever(vector_store)

@pytest.fixture(scope="session")
def reranker():
    return RerankerFilter()

@pytest.fixture(scope="session")
def context_builder():
    return ContextBuilder()

@pytest.fixture(scope="session")
def section_metadata():
    sec_file = PROJECT_ROOT / "section_metadata.json"
    with open(sec_file, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def judgment_metadata():
    jdg_file = PROJECT_ROOT / "judgment_metadata.json"
    with open(jdg_file, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture(scope="session")
def multi_agent_system():
    return MultiAgentLegalSystem()

@pytest.fixture(scope="session")
def orchestrator():
    return Phase15WorkflowOrchestrator()

@pytest.fixture(scope="session")
def api_client():
    return TestClient(app)

# Standard Test Case Fixtures
@pytest.fixture
def mutual_consent_case_text():
    return (
        "I was married in January 2021 under the Hindu Marriage Act. My husband and I have been living "
        "separately for over two years since March 2023. We have executed a formal settlement agreement "
        "resolving all permanent alimony and return of stridhan. We now seek dissolution of our marriage "
        "by mutual consent under Section 13B and request waiver of the statutory 6-month cooling-off period."
    )

@pytest.fixture
def cruelty_divorce_case_text():
    return (
        "Marriage took place in November 2019 according to Hindu rites. The wife subjected the husband and his "
        "aged parents to severe mental cruelty by lodging unfounded criminal complaints under Section 498A IPC "
        "and Section 125 CrPC. After a full trial, the Judicial Magistrate acquitted the husband and family with a "
        "finding of false and vindictive prosecution. The husband now petitions for divorce on the ground of cruelty "
        "under Section 13(1)(ia) of the Hindu Marriage Act, 1955."
    )

@pytest.fixture
def pwdva_case_text():
    return (
        "The applicant wife was married in December 2020 and lived with her husband and in-laws in a joint family residence. "
        "She was subjected to continuous verbal, physical, and economic harassment, and was subsequently locked out and "
        "dispossessed from the matrimonial home. She files an application under the Protection of Women from Domestic Violence "
        "Act 2005 seeking protection orders, right of residence in the shared household under Section 17 and Section 19, and "
        "interim monetary relief under Section 20."
    )

@pytest.fixture
def child_custody_case_text():
    return (
        "Father and mother are locked in matrimonial litigation under the Hindu Marriage Act. They have a 6-year-old child. "
        "The mother unilaterally relocated to another city and denies all visitation to the father. The father petitions under "
        "the Guardian and Wards Act, 1890 and Section 26 of the Hindu Marriage Act seeking defined custody and visitation rights, "
        "asserting the doctrine of the paramount welfare of the child."
    )

@pytest.fixture
def out_of_scope_cases():
    return [
        "A technology company claims another firm infringed its semiconductor manufacturing patent under patent law.",
        "Defendant was caught driving at 120 km/h in a 60 km/h speed zone and received a traffic fine.",
        "A group of traders lost money in a decentralized cryptocurrency wallet hack and wants money recovered.",
        "A commercial breach of contract between two logistics companies regarding delivery of steel rods."
    ]

@pytest.fixture
def trivial_cases():
    return [
        "hello",
        "hi can you help",
        "legal help please",
        "divorce",
        "test query 123",
        "asdfghjkl"
    ]
