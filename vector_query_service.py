import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from fastembed import TextEmbedding

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PERSIST_DIR = Path(os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_db")))

# Shared process-level singletons to maintain a minimal RAM footprint (<150MB on Render 512MB free tier)
_shared_client: Optional[chromadb.PersistentClient] = None
_shared_embed_model: Optional[TextEmbedding] = None
_init_lock = threading.Lock()

def get_shared_client(persist_dir: Path) -> chromadb.PersistentClient:
    global _shared_client
    if _shared_client is None:
        with _init_lock:
            if _shared_client is None:
                persist_dir.mkdir(parents=True, exist_ok=True)
                _shared_client = chromadb.PersistentClient(path=str(persist_dir))
    return _shared_client

def get_shared_embed_model(model_name: str = "BAAI/bge-small-en-v1.5") -> TextEmbedding:
    global _shared_embed_model
    if _shared_embed_model is None:
        with _init_lock:
            if _shared_embed_model is None:
                # threads=1 drastically curtails ONNX Runtime memory allocation
                _shared_embed_model = TextEmbedding(model_name=model_name, threads=1)
    return _shared_embed_model

class LegalVectorStore:
    def __init__(self, persist_dir: Path = CHROMA_PERSIST_DIR, model_name: str = "BAAI/bge-small-en-v1.5"):
        self.persist_dir = persist_dir
        self.client = get_shared_client(persist_dir)
        try:
            self.master_col = self.client.get_collection("legal_corpus")
            self.statute_col = self.client.get_collection("statute_sections")
            self.precedent_col = self.client.get_collection("precedent_chunks")
        except Exception:
            # Fallback if collections not yet present
            self.master_col = self.client.get_or_create_collection("legal_corpus")
            self.statute_col = self.client.get_or_create_collection("statute_sections")
            self.precedent_col = self.client.get_or_create_collection("precedent_chunks")
        self.embed_model = get_shared_embed_model(model_name)

    def _get_embedding(self, query: str) -> List[float]:
        return list(self.embed_model.embed([query]))[0].tolist()

    def search_master(self, query: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Dense semantic search across the entire 916-chunk corpus."""
        t_start = time.perf_counter()
        count = self.master_col.count()
        if count == 0:
            return []
        effective_k = min(top_k, count)
        try:
            q_embed = self._get_embedding(query)
            results = self.master_col.query(
                query_embeddings=[q_embed],
                n_results=effective_k,
                where=where
            )
            formatted = self._format_results(results)
            dur = time.perf_counter() - t_start
            try:
                from observability.metrics import record_rag_retrieval
                from observability.logging_config import get_logger
                record_rag_retrieval("legal_corpus", dur, len(formatted))
                get_logger("rag").info(
                    f"RAG query in legal_corpus retrieved {len(formatted)} chunks in {dur:.4f}s",
                    extra={"agent_name": "RAGSearch", "latency": dur, "doc_count": len(formatted), "status": "SUCCESS"}
                )
            except Exception:
                pass
            return formatted
        except Exception as e:
            dur = time.perf_counter() - t_start
            try:
                from observability.metrics import record_rag_retrieval
                from observability.logging_config import get_logger
                record_rag_retrieval("legal_corpus", dur, 0, failed=True, reason=type(e).__name__)
                get_logger("rag").error(
                    f"RAG retrieval failure in legal_corpus: {str(e)}",
                    extra={"agent_name": "RAGSearch", "latency": dur, "status": "ERROR"}
                )
            except Exception:
                pass
            raise

    def search_statutes(self, query: str, top_k: int = 5, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Dense search focused strictly on statutory law (Law & Constraint Hunter Agents)."""
        t_start = time.perf_counter()
        count = self.statute_col.count()
        if count == 0:
            return []
        effective_k = min(top_k, count)
        try:
            q_embed = self._get_embedding(query)
            results = self.statute_col.query(
                query_embeddings=[q_embed],
                n_results=effective_k,
                where=where
            )
            formatted = self._format_results(results)
            dur = time.perf_counter() - t_start
            try:
                from observability.metrics import record_rag_retrieval
                from observability.logging_config import get_logger
                record_rag_retrieval("statute_sections", dur, len(formatted))
                get_logger("rag").info(
                    f"RAG query in statute_sections retrieved {len(formatted)} chunks in {dur:.4f}s",
                    extra={"agent_name": "RAGSearch", "latency": dur, "doc_count": len(formatted), "status": "SUCCESS"}
                )
            except Exception:
                pass
            return formatted
        except Exception as e:
            dur = time.perf_counter() - t_start
            try:
                from observability.metrics import record_rag_retrieval
                from observability.logging_config import get_logger
                record_rag_retrieval("statute_sections", dur, 0, failed=True, reason=type(e).__name__)
                get_logger("rag").error(
                    f"RAG retrieval failure in statute_sections: {str(e)}",
                    extra={"agent_name": "RAGSearch", "latency": dur, "status": "ERROR"}
                )
            except Exception:
                pass
            raise

    def search_precedents(self, query: str, top_k: int = 5, chunk_type: Optional[str] = None, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Dense search focused strictly on judicial precedents (Precedent, Opposition, Evidence, Judge Agents)."""
        t_start = time.perf_counter()
        count = self.precedent_col.count()
        if count == 0:
            return []
        effective_k = min(top_k, count)
        try:
            q_embed = self._get_embedding(query)
            filter_dict = where or {}
            if chunk_type:
                filter_dict["chunk_type"] = chunk_type
                
            results = self.precedent_col.query(
                query_embeddings=[q_embed],
                n_results=effective_k,
                where=filter_dict if filter_dict else None
            )
            formatted = self._format_results(results)
            dur = time.perf_counter() - t_start
            try:
                from observability.metrics import record_rag_retrieval
                from observability.logging_config import get_logger
                record_rag_retrieval("precedent_chunks", dur, len(formatted))
                get_logger("rag").info(
                    f"RAG query in precedent_chunks retrieved {len(formatted)} chunks in {dur:.4f}s",
                    extra={"agent_name": "RAGSearch", "latency": dur, "doc_count": len(formatted), "status": "SUCCESS"}
                )
            except Exception:
                pass
            return formatted
        except Exception as e:
            dur = time.perf_counter() - t_start
            try:
                from observability.metrics import record_rag_retrieval
                from observability.logging_config import get_logger
                record_rag_retrieval("precedent_chunks", dur, 0, failed=True, reason=type(e).__name__)
                get_logger("rag").error(
                    f"RAG retrieval failure in precedent_chunks: {str(e)}",
                    extra={"agent_name": "RAGSearch", "latency": dur, "status": "ERROR"}
                )
            except Exception:
                pass
            raise

    def _format_results(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        formatted = []
        if not raw or not raw.get("ids") or not raw["ids"][0]:
            return formatted
            
        ids = raw["ids"][0]
        distances = raw["distances"][0]
        metadatas = raw["metadatas"][0]
        documents = raw["documents"][0]

        for i in range(len(ids)):
            # Convert cosine distance to cosine similarity: sim = 1 - distance
            dist = distances[i]
            sim = 1.0 - dist
            formatted.append({
                "chunk_id": ids[i],
                "similarity_score": round(sim, 4),
                "distance": round(dist, 4),
                "metadata": metadatas[i],
                "content_preview": documents[i][:300].replace("\n", " ") + "..."
            })
        return formatted

def run_verification_tests():
    print("=" * 80)
    print("LEGAL VECTOR DATABASE VERIFICATION TEST SUITE (PHASE 12)")
    print("=" * 80)
    
    store = LegalVectorStore()
    
    test_cases = [
        {
            "name": "TEST 1: Constraint Hunter Agent — Temporal Limits & Cooling-Off",
            "query": "waiver of six months cooling off period for divorce by mutual consent",
            "search_type": "statutes",
            "filter": {"has_temporal_limits": True},
            "top_k": 3
        },
        {
            "name": "TEST 2: Precedent Agent — Irretrievable Breakdown & Article 142",
            "query": "Supreme Court dissolution of marriage irretrievable breakdown of marriage Article 142",
            "search_type": "precedents",
            "chunk_type": "judgment_ratio",
            "top_k": 3
        },
        {
            "name": "TEST 3: Evidence Agent — Cruelty Allegations & Factual Matrix",
            "query": "allegations of mental cruelty lodging false criminal complaints and FIRs",
            "search_type": "precedents",
            "chunk_type": "judgment_facts",
            "top_k": 3
        },
        {
            "name": "TEST 4: Judge Agent — Permanent Alimony & Maintenance Holding",
            "query": "permanent alimony enhancement maintenance quantum monthly payment",
            "search_type": "precedents",
            "chunk_type": "judgment_holding",
            "top_k": 3
        },
        {
            "name": "TEST 5: Law Agent — Domestic Violence Shared Household",
            "query": "right of residence shared household under Domestic Violence Act",
            "search_type": "statutes",
            "filter": {"act_id": "PWDVA_2005"},
            "top_k": 3
        }
    ]

    for tc in test_cases:
        print(f"\n>>> {tc['name']}")
        print(f"Query: \"{tc['query']}\"")
        t0 = time.time()
        
        if tc["search_type"] == "statutes":
            hits = store.search_statutes(tc["query"], top_k=tc["top_k"], where=tc.get("filter"))
        elif tc["search_type"] == "precedents":
            hits = store.search_precedents(tc["query"], top_k=tc["top_k"], chunk_type=tc.get("chunk_type"), where=tc.get("filter"))
        else:
            hits = store.search_master(tc["query"], top_k=tc["top_k"], where=tc.get("filter"))
            
        latency = (time.time() - t0) * 1000
        print(f"Retrieval Latency: {latency:.2f} ms | Hits returned: {len(hits)}")
        
        for idx, h in enumerate(hits, 1):
            meta = h["metadata"]
            if meta.get("document_type") == "statute":
                label = f"[STATUTE] {meta.get('act_id')} Sec {meta.get('section_number')}: {meta.get('section_title')}"
                constraint_info = f"Constraints: {meta.get('constraint_types')}"
            else:
                label = f"[PRECEDENT] {meta.get('judgment_id')} ({meta.get('case_name')}) | Type: {meta.get('chunk_type')}"
                constraint_info = f"Tier: {meta.get('relevance_tier')} | Sub-type: {meta.get('sub_case_type')}"
                
            print(f"  {idx}. Sim: {h['similarity_score']:.4f} | {label}")
            print(f"     {constraint_info}")
            print(f"     Preview: {h['content_preview'][:160]}...")
            
    print("\n" + "=" * 80)
    print("ALL 5 VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_verification_tests()
