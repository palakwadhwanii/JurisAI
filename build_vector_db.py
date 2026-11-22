import json
import time
from pathlib import Path
import chromadb
from fastembed import TextEmbedding

BASE_DIR = Path(__file__).resolve().parent
CHUNKS_FILE = BASE_DIR / "chunks" / "all_legal_chunks.json"
CHROMA_PERSIST_DIR = BASE_DIR / "chroma_db"

def prepare_metadata(chunk):
    """
    Ensure all metadata values conform to ChromaDB types:
    str, int, float, or bool.
    """
    meta = {}
    doc_type = chunk.get("document_type", "statute")
    meta["document_type"] = doc_type
    meta["chunk_id"] = chunk["chunk_id"]
    meta["char_count"] = int(chunk.get("char_count", len(chunk["content"])))
    meta["token_estimate"] = int(chunk.get("token_estimate", len(chunk["content"]) // 4))

    if doc_type == "statute":
        meta["act_id"] = str(chunk.get("act_id", ""))
        meta["act_name"] = str(chunk.get("act_name", ""))
        meta["year"] = int(chunk.get("year", 0))
        meta["domain"] = str(chunk.get("domain", "Family Law"))
        meta["category"] = str(chunk.get("category", "Family Law"))
        meta["section_number"] = str(chunk.get("section_number", ""))
        meta["section_title"] = str(chunk.get("section_title", ""))
        meta["has_provisos"] = bool(chunk.get("has_provisos", False))
        meta["has_temporal_limits"] = bool(chunk.get("has_temporal_limits", False))
        meta["has_bars"] = bool(chunk.get("has_bars", False))
        # Summary of constraints
        constraints = chunk.get("constraints_detected", [])
        meta["constraint_count"] = len(constraints)
        if constraints:
            meta["constraint_types"] = ",".join(sorted(list(set(c["constraint_type"] for c in constraints))))
        else:
            meta["constraint_types"] = "NONE"
            
    elif doc_type == "precedent":
        meta["judgment_id"] = str(chunk.get("judgment_id", ""))
        meta["case_name"] = str(chunk.get("case_name", ""))
        meta["year"] = int(chunk.get("year", 0))
        meta["sub_case_type"] = str(chunk.get("sub_case_type", ""))
        meta["relevance_tier"] = str(chunk.get("relevance_tier", ""))
        meta["chunk_type"] = str(chunk.get("chunk_type", ""))
        meta["scr_citation"] = str(chunk.get("scr_citation", ""))
        meta["insc_citation"] = str(chunk.get("insc_citation", ""))
        bench = chunk.get("bench", [])
        meta["bench"] = ", ".join(bench) if isinstance(bench, list) else str(bench)
        primary_agents = chunk.get("primary_agents", [])
        meta["primary_agents"] = ",".join(primary_agents) if isinstance(primary_agents, list) else str(primary_agents)
        
    return meta

def main():
    print("=" * 70)
    print("PHASE 12: Embeddings & Vector Database Indexing")
    print(f"Embedding Model: BAAI/bge-small-en-v1.5 (FastEmbed ONNX, 384-dim)")
    print(f"Vector Database: ChromaDB PersistentClient at {CHROMA_PERSIST_DIR}")
    print("=" * 70)

    # 1. Load Chunks
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    # 2. Initialize Chroma Client
    CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

    # Reset/Create Collections:
    # 1. Master collection: legal_corpus (all 916 chunks)
    # 2. Statute collection: statute_sections (461 chunks)
    # 3. Precedent collection: precedent_chunks (455 chunks)
    for col_name in ["legal_corpus", "statute_sections", "precedent_chunks"]:
        try:
            client.delete_collection(col_name)
            print(f"Cleared existing collection: {col_name}")
        except Exception:
            pass

    master_col = client.create_collection(
        name="legal_corpus",
        metadata={"hnsw:space": "cosine", "description": "Master Unified Legal Corpus"}
    )
    statute_col = client.create_collection(
        name="statute_sections",
        metadata={"hnsw:space": "cosine", "description": "Statutory Sections for Law & Constraint Hunter Agents"}
    )
    precedent_col = client.create_collection(
        name="precedent_chunks",
        metadata={"hnsw:space": "cosine", "description": "Judicial Precedents for Precedent, Evidence, Opposition, Judge Agents"}
    )

    # 3. Initialize Embedding Model
    print("\nLoading FastEmbed model 'BAAI/bge-small-en-v1.5'...")
    embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # 4. Batch Embed & Index
    batch_size = 64
    total = len(chunks)
    print(f"Generating embeddings and indexing into ChromaDB in batches of {batch_size}...")

    t0 = time.time()
    for i in range(0, total, batch_size):
        batch = chunks[i:i + batch_size]
        ids = [c["chunk_id"] for c in batch]
        documents = [c["content"] for c in batch]
        metadatas = [prepare_metadata(c) for c in batch]

        # Generate embeddings
        embeddings_gen = embed_model.embed(documents)
        embeddings = [e.tolist() for e in embeddings_gen]

        # Add to Master collection
        master_col.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        # Route to dedicated collections
        statute_batch_ids = []
        statute_docs = []
        statute_embeds = []
        statute_metas = []

        precedent_batch_ids = []
        precedent_docs = []
        precedent_embeds = []
        precedent_metas = []

        for idx, c in enumerate(batch):
            if c.get("document_type") == "statute":
                statute_batch_ids.append(ids[idx])
                statute_docs.append(documents[idx])
                statute_embeds.append(embeddings[idx])
                statute_metas.append(metadatas[idx])
            else:
                precedent_batch_ids.append(ids[idx])
                precedent_docs.append(documents[idx])
                precedent_embeds.append(embeddings[idx])
                precedent_metas.append(metadatas[idx])

        if statute_batch_ids:
            statute_col.add(
                ids=statute_batch_ids,
                documents=statute_docs,
                embeddings=statute_embeds,
                metadatas=statute_metas
            )

        if precedent_batch_ids:
            precedent_col.add(
                ids=precedent_batch_ids,
                documents=precedent_docs,
                embeddings=precedent_embeds,
                metadatas=precedent_metas
            )

        processed = min(i + batch_size, total)
        print(f"  Processed {processed}/{total} chunks ({(processed/total)*100:.1f}%)")

    elapsed = time.time() - t0
    print(f"\n[COMPLETED] Successfully embedded and indexed {total} chunks in {elapsed:.2f} seconds!")
    print(f"Average throughput: {total / elapsed:.1f} chunks/sec")
    print(f"Master Collection count: {master_col.count()}")
    print(f"Statute Collection count: {statute_col.count()}")
    print(f"Precedent Collection count: {precedent_col.count()}")

if __name__ == "__main__":
    main()
