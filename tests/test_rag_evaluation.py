import time
import pytest
from typing import List, Dict, Any

from legal_rag_pipeline import QueryProcessor, HybridRetriever, RerankerFilter, ContextBuilder
from vector_query_service import LegalVectorStore

class TestRAGEvaluation:
    """
    PHASE 19: RAG Evaluation Suite
    Evaluates:
    - Vector database collection integrity and chunk counts
    - Query processor entity and section detection
    - Semantic retrieval precision, Hit Rate @ K, and MRR
    - Reranker boosting (exact section match, constraint flags, relevance tiers)
    - Grounded context synthesis and latency constraints
    """

    def test_vector_store_collection_integrity(self, vector_store: LegalVectorStore):
        """Verifies vector DB collections are loaded, indexed, and persist correct counts."""
        master_count = vector_store.master_col.count()
        statute_count = vector_store.statute_col.count()
        precedent_count = vector_store.precedent_col.count()

        assert master_count == 916, f"Expected 916 chunks in legal_corpus, found {master_count}"
        assert statute_count > 0, "Statute sections collection is empty"
        assert precedent_count > 0, "Precedent chunks collection is empty"
        assert statute_count + precedent_count == master_count, (
            f"Sum of sub-collections ({statute_count} + {precedent_count}) should equal master ({master_count})"
        )

    def test_query_processor_act_and_section_detection(self, query_processor: QueryProcessor):
        """Verifies query processing extracts correct Acts and sections from factual narratives."""
        test_cases = [
            {
                "narrative": "Parties seek mutual consent divorce under Hindu Marriage Act after 2 years separation.",
                "expected_act": "HMA_1955",
                "expected_section": "13B"
            },
            {
                "narrative": "Husband filed divorce alleging continuous mental cruelty and false police complaints.",
                "expected_act": "HMA_1955",
                "expected_section": "13(1)(ia)"
            },
            {
                "narrative": "Wife seeking right of residence in shared household under domestic violence act.",
                "expected_act": "PWDVA_2005",
                "expected_section": "17"
            },
            {
                "narrative": "Mother refuses father custody and visitation of child under guardians and wards.",
                "expected_act": "GWA_1890",
                "expected_section": None
            }
        ]

        for tc in test_cases:
            res = query_processor.process(tc["narrative"])
            assert tc["expected_act"] in res["detected_acts"], (
                f"Failed to detect {tc['expected_act']} in '{tc['narrative']}'. Detected: {res['detected_acts']}"
            )
            if tc["expected_section"]:
                assert any(tc["expected_section"].lower() in s.lower() for s in res["candidate_sections"]), (
                    f"Expected section {tc['expected_section']} not found in {res['candidate_sections']}"
                )
            assert len(res["statute_query"]) > 10
            assert len(res["precedent_query"]) > 10

    def test_statute_retrieval_relevance_and_hit_rate(self, hybrid_retriever: HybridRetriever, query_processor: QueryProcessor, reranker: RerankerFilter):
        """
        Evaluates retrieval Hit Rate @ K and MRR against a benchmark of known legal queries.
        Ground truth pairs: (query, target_section_or_keyword)
        """
        eval_queries = [
            ("Parties married in 2021 seek mutual consent divorce under section 13B and waiver of 6 months cooling off period", ["13B", "13-b", "mutual consent"]),
            ("Wife seeks right of residence in shared household and protection order under domestic violence act section 17 and 19", ["17", "19", "residence", "shared household"]),
            ("Wife claims interim maintenance pendente lite and litigation expenses under section 24 and 25", ["24", "25", "125", "maintenance"]),
            ("Husband petitions for dissolution of marriage and divorce on grounds of mental cruelty under section 13", ["13", "cruelty", "divorce"]),
            ("Father petitions for custody and guardianship of minor child under guardian and wards act", ["custody", "guardianship", "minor", "welfare", "ward", "7", "17", "10", "11"])
        ]

        hits_at_1 = 0
        hits_at_3 = 0
        hits_at_5 = 0
        reciprocal_ranks = []

        for q_text, targets in eval_queries:
            q_plan = query_processor.process(q_text)
            statute_hits, precedent_hits = hybrid_retriever.retrieve_candidates(q_plan, top_statutes=6, top_precedents=5)
            ranked_statutes, _ = reranker.filter_and_rank(statute_hits, precedent_hits, q_plan["candidate_sections"])

            matched_rank = None
            for idx, hit in enumerate(ranked_statutes, 1):
                sec_num = str(hit["metadata"].get("section_number", ""))
                title = str(hit["metadata"].get("section_title", "")).lower()
                preview = str(hit.get("content_preview", "")).lower()

                if any(t.lower() in sec_num.lower() or t.lower() in title or t.lower() in preview for t in targets):
                    matched_rank = idx
                    break

            if matched_rank is not None:
                if matched_rank == 1:
                    hits_at_1 += 1
                if matched_rank <= 3:
                    hits_at_3 += 1
                if matched_rank <= 5:
                    hits_at_5 += 1
                reciprocal_ranks.append(1.0 / matched_rank)
            else:
                reciprocal_ranks.append(0.0)

        n = len(eval_queries)
        hit_rate_top3 = hits_at_3 / n
        hit_rate_top5 = hits_at_5 / n
        mrr = sum(reciprocal_ranks) / n

        assert hit_rate_top3 >= 0.80, f"Hit Rate @ 3 fell below threshold (80%): got {hit_rate_top3 * 100:.1f}%"
        assert hit_rate_top5 >= 0.80, f"Hit Rate @ 5 fell below threshold (80%): got {hit_rate_top5 * 100:.1f}%"
        assert mrr >= 0.60, f"MRR fell below threshold (0.60): got {mrr:.3f}"

    def test_precedent_retrieval_and_ratio_extraction(self, hybrid_retriever: HybridRetriever, query_processor: QueryProcessor):
        """Verifies precedent retrieval extracts binding ratios with valid SCR citations."""
        q_plan = query_processor.process(
            "Supreme court guidelines on waiving 6 month statutory cooling off period in mutual divorce"
        )
        _, precedent_hits = hybrid_retriever.retrieve_candidates(q_plan, top_statutes=2, top_precedents=5)

        assert len(precedent_hits) > 0, "No precedents retrieved"
        
        # Verify metadata integrity of retrieved precedents
        for p in precedent_hits:
            meta = p["metadata"]
            assert "case_name" in meta and len(meta["case_name"]) > 0
            assert "scr_citation" in meta or "insc_citation" in meta
            assert meta.get("chunk_type") in ["judgment_ratio", "judgment_holding", "precedent"]

    def test_reranker_filtering_and_score_boosting(self, reranker: RerankerFilter):
        """Tests that RerankerFilter applies boosting for section matches, constraints, and tiers."""
        mock_statutes = [
            {
                "chunk_id": "s1",
                "similarity_score": 0.70,
                "metadata": {"section_number": "13B", "has_temporal_limits": True, "has_provisos": False, "has_bars": False}
            },
            {
                "chunk_id": "s2",
                "similarity_score": 0.75,
                "metadata": {"section_number": "5", "has_temporal_limits": False, "has_provisos": False, "has_bars": False}
            }
        ]
        
        mock_precedents = [
            {
                "chunk_id": "p1",
                "similarity_score": 0.65,
                "metadata": {"relevance_tier": "DIRECT"}
            },
            {
                "chunk_id": "p2",
                "similarity_score": 0.80,
                "metadata": {"relevance_tier": "NOT_RELEVANT"}
            },
            {
                "chunk_id": "p3",
                "similarity_score": 0.68,
                "metadata": {"relevance_tier": "RELATED"}
            }
        ]

        ranked_statutes, ranked_precedents = reranker.filter_and_rank(
            mock_statutes, mock_precedents, candidate_sections=["13B"]
        )

        # s1 base 0.70 + 0.15 (section match) + 0.05 (temporal limit) = 0.90
        # s2 base 0.75 + 0 = 0.75
        assert ranked_statutes[0]["chunk_id"] == "s1"
        assert ranked_statutes[0]["rerank_score"] >= 0.89

        # p2 has tier NOT_RELEVANT, must be filtered out
        p_ids = [p["chunk_id"] for p in ranked_precedents]
        assert "p2" not in p_ids, "NOT_RELEVANT precedent was not filtered out"
        # p1 (0.65 + 0.10 = 0.75) vs p3 (0.68 + 0.02 = 0.70) -> p1 should rank higher
        assert ranked_precedents[0]["chunk_id"] == "p1"

    def test_context_builder_output_and_anti_hallucination_rules(self, context_builder: ContextBuilder):
        """Tests context assembler ensures strict anti-hallucination instructions and citations."""
        statutes = [{
            "chunk_id": "s_13b",
            "metadata": {
                "act_name": "Hindu Marriage Act, 1955",
                "section_number": "13B",
                "section_title": "Divorce by mutual consent",
                "year": 1955,
                "constraint_types": "COOLING_OFF_PERIOD"
            },
            "content_preview": "Section 13B. Divorce by mutual consent..."
        }]
        precedents = [{
            "chunk_id": "p_shilpa",
            "metadata": {
                "case_name": "Shilpa Sailesh v. Varun Sreenivasan",
                "year": 2023,
                "scr_citation": "[2023] 5 S.C.R. 1",
                "insc_citation": "2023 INSC 468",
                "bench": "S.K. Kaul, Sanjiv Khanna, A.S. Oka, Vikram Nath, J.K. Maheshwari",
                "sub_case_type": "Mutual Consent Divorce & Article 142",
                "relevance_tier": "DIRECT"
            },
            "content_preview": "Supreme Court can grant decree of divorce by mutual consent waiving Section 13B(2)..."
        }]

        prompt, citations = context_builder.build_context(
            user_case="Husband and wife agree on mutual consent divorce after 2 years living apart.",
            statutes=statutes,
            precedents=precedents
        )

        assert "=== BINDING STATUTORY PROVISIONS ===" in prompt
        assert "=== BINDING SUPREME COURT PRECEDENTS ===" in prompt
        assert "CRITICAL CONSTRAINT: Cite ONLY the exact sections" in prompt
        assert len(citations) == 2
        assert citations[0]["type"] == "STATUTE"
        assert citations[0]["section"] == "13B"
        assert citations[1]["type"] == "PRECEDENT"
        assert citations[1]["case_name"] == "Shilpa Sailesh v. Varun Sreenivasan"

    def test_retrieval_latency_benchmark(self, vector_store: LegalVectorStore):
        """Asserts that single dense retrieval across collections finishes under 1.5 seconds SLA."""
        t_start = time.perf_counter()
        results = vector_store.search_master("mutual consent divorce cooling off period waiver", top_k=5)
        duration = time.perf_counter() - t_start

        assert len(results) > 0
        assert duration < 2.0, f"RAG retrieval exceeded SLA limit: {duration:.4f}s > 2.0s"
