import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JUDGMENT_METADATA_FILE = BASE_DIR / "judgment_metadata.json"
STATUTE_CHUNKS_FILE = BASE_DIR / "chunks" / "statute_chunks.json"
OUTPUT_JUDGMENT_CHUNKS = BASE_DIR / "chunks" / "judgment_chunks.json"
OUTPUT_ALL_CHUNKS = BASE_DIR / "chunks" / "all_legal_chunks.json"

def format_acts_sections(acts_map):
    parts = []
    for act, secs in acts_map.items():
        if secs:
            parts.append(f"{act} [Sections: {', '.join(secs)}]")
        else:
            parts.append(act)
    return "; ".join(parts) if parts else "None specifically cited"

def generate_judgment_chunks(d):
    jid = d["judgment_id"]
    name = d["case_name"]
    year = d["year"]
    bench_str = ", ".join(d.get("bench", [])) if d.get("bench") else "Supreme Court Bench"
    scr = d.get("scr_citation") or "N/A"
    insc = d.get("insc_citation") or jid.replace("_", " ")
    appeal = d.get("appeal_number") or "N/A"
    tier = d["relevance_tier"]
    stype = d["sub_case_type"]
    reason = d["relevance_reason"]
    acts_sec_str = format_acts_sections(d.get("acts_and_sections_invoked", {}))
    
    issues_list = d.get("legal_issues", [])
    if isinstance(issues_list, list):
        issues_text = "\n".join([f"- {iss}" for iss in issues_list])
    else:
        issues_text = str(issues_list)
        
    facts_text = d.get("facts_summary", "")
    ratio_text = d.get("legal_principles", "")
    holding_text = d.get("decision_holding", "")
    
    chunks = []
    
    # -------------------------------------------------------------
    # 1. ISSUE CHUNK (Case Manager, Law Agent, Auditor Agent)
    # -------------------------------------------------------------
    issue_content = (
        f"[PRECEDENT METADATA & ISSUES]\n"
        f"Case: {name}\n"
        f"Citation: {scr} | {insc}\n"
        f"Appeal: {appeal}\n"
        f"Year: {year} | Bench: {bench_str}\n"
        f"Sub-Case Type: {stype}\n"
        f"Relevance Tier: {tier} ({reason})\n"
        f"Acts and Sections Invoked: {acts_sec_str}\n\n"
        f"LEGAL ISSUES FOR CONSIDERATION:\n{issues_text}"
    )
    chunks.append({
        "chunk_id": f"{jid}_ISSUE",
        "document_type": "precedent",
        "judgment_id": jid,
        "case_name": name,
        "year": year,
        "bench": d.get("bench", []),
        "scr_citation": scr,
        "insc_citation": insc,
        "sub_case_type": stype,
        "relevance_tier": tier,
        "chunk_type": "judgment_issue",
        "primary_agents": ["CaseManagerAgent", "LawAgent", "AuditorAgent"],
        "content": issue_content,
        "char_count": len(issue_content),
        "token_estimate": len(issue_content) // 4,
        "acts_and_sections": d.get("acts_and_sections_invoked", {})
    })
    
    # -------------------------------------------------------------
    # 2. FACTS CHUNK (Evidence Agent, Case Manager Agent)
    # -------------------------------------------------------------
    facts_content = (
        f"[PRECEDENT FACTUAL MATRIX]\n"
        f"Case: {name} ({year})\n"
        f"Sub-Case Type: {stype} | Relevance Tier: {tier}\n"
        f"Statutory Context: {acts_sec_str}\n\n"
        f"FACTS SUMMARY & MATRIMONIAL DISPUTE BACKGROUND:\n{facts_text}"
    )
    chunks.append({
        "chunk_id": f"{jid}_FACTS",
        "document_type": "precedent",
        "judgment_id": jid,
        "case_name": name,
        "year": year,
        "bench": d.get("bench", []),
        "scr_citation": scr,
        "insc_citation": insc,
        "sub_case_type": stype,
        "relevance_tier": tier,
        "chunk_type": "judgment_facts",
        "primary_agents": ["EvidenceAgent", "CaseManagerAgent"],
        "content": facts_content,
        "char_count": len(facts_content),
        "token_estimate": len(facts_content) // 4,
        "acts_and_sections": d.get("acts_and_sections_invoked", {})
    })
    
    # -------------------------------------------------------------
    # 3. RATIO CHUNK (Precedent Agent, Opposition Agent, Constraint Hunter)
    # -------------------------------------------------------------
    ratio_content = (
        f"[PRECEDENT RATIO DECIDENDI & LEGAL PRINCIPLES]\n"
        f"Case: {name} ({year})\n"
        f"Citation: {scr} | {insc}\n"
        f"Sub-Case Type: {stype}\n"
        f"Acts and Sections Invoked: {acts_sec_str}\n\n"
        f"LEGAL PRINCIPLES ESTABLISHED (RATIO DECIDENDI):\n{ratio_text}\n\n"
        f"STATUTORY & JUDICIAL APPLICATION:\n"
        f"- Substantive relevance: {reason}\n"
        f"- Decided by: {bench_str}"
    )
    chunks.append({
        "chunk_id": f"{jid}_RATIO",
        "document_type": "precedent",
        "judgment_id": jid,
        "case_name": name,
        "year": year,
        "bench": d.get("bench", []),
        "scr_citation": scr,
        "insc_citation": insc,
        "sub_case_type": stype,
        "relevance_tier": tier,
        "chunk_type": "judgment_ratio",
        "primary_agents": ["PrecedentAgent", "OppositionAgent", "ConstraintHunterAgent"],
        "content": ratio_content,
        "char_count": len(ratio_content),
        "token_estimate": len(ratio_content) // 4,
        "acts_and_sections": d.get("acts_and_sections_invoked", {})
    })
    
    # -------------------------------------------------------------
    # 4. HOLDING CHUNK (Judge Agent, Opposition Agent)
    # -------------------------------------------------------------
    holding_content = (
        f"[PRECEDENT HOLDING & FINAL ORDERS]\n"
        f"Case: {name} ({year})\n"
        f"Citation: {scr} | {insc}\n"
        f"Sub-Case Type: {stype} | Relevance Tier: {tier}\n\n"
        f"DECISION & ORDER OF THE SUPREME COURT:\n{holding_text}"
    )
    chunks.append({
        "chunk_id": f"{jid}_HOLDING",
        "document_type": "precedent",
        "judgment_id": jid,
        "case_name": name,
        "year": year,
        "bench": d.get("bench", []),
        "scr_citation": scr,
        "insc_citation": insc,
        "sub_case_type": stype,
        "relevance_tier": tier,
        "chunk_type": "judgment_holding",
        "primary_agents": ["JudgeAgent", "OppositionAgent"],
        "content": holding_content,
        "char_count": len(holding_content),
        "token_estimate": len(holding_content) // 4,
        "acts_and_sections": d.get("acts_and_sections_invoked", {})
    })
    
    # -------------------------------------------------------------
    # 5. SYNTHESIS SUMMARY CHUNK (Holistic Single-Pass Retrieval)
    # -------------------------------------------------------------
    summary_content = (
        f"[PRECEDENT COMPLETE LEGAL DIGEST]\n"
        f"Case: {name}\n"
        f"Citation: {scr} : {insc} | Date: {d.get('date', 'N/A')}\n"
        f"Bench: {bench_str}\n"
        f"Sub-Case: {stype} | Relevance: {tier}\n"
        f"Acts and Sections: {acts_sec_str}\n\n"
        f"FACTS:\n{facts_text}\n\n"
        f"ISSUES:\n{issues_text}\n\n"
        f"HOLDING:\n{holding_text}\n\n"
        f"RATIO DECIDENDI:\n{ratio_text}"
    )
    chunks.append({
        "chunk_id": f"{jid}_SUMMARY",
        "document_type": "precedent",
        "judgment_id": jid,
        "case_name": name,
        "year": year,
        "bench": d.get("bench", []),
        "scr_citation": scr,
        "insc_citation": insc,
        "sub_case_type": stype,
        "relevance_tier": tier,
        "chunk_type": "judgment_summary",
        "primary_agents": ["CaseManagerAgent", "PrecedentAgent", "AuditorAgent"],
        "content": summary_content,
        "char_count": len(summary_content),
        "token_estimate": len(summary_content) // 4,
        "acts_and_sections": d.get("acts_and_sections_invoked", {})
    })
    
    return chunks

def main():
    print("Starting Phase 11: Judicial Precedent Document Processing...")
    
    with open(JUDGMENT_METADATA_FILE, "r", encoding="utf-8") as f:
        judgments = json.load(f)
        
    all_judgment_chunks = []
    for d in judgments:
        chunks = generate_judgment_chunks(d)
        all_judgment_chunks.extend(chunks)
        
    OUTPUT_JUDGMENT_CHUNKS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JUDGMENT_CHUNKS, "w", encoding="utf-8") as f:
        json.dump(all_judgment_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"[SUCCESS] Generated {len(all_judgment_chunks)} semantic precedent chunks for {len(judgments)} judgments!")
    print(f"Saved to: {OUTPUT_JUDGMENT_CHUNKS}")
    
    # Now merge into all_legal_chunks.json
    with open(STATUTE_CHUNKS_FILE, "r", encoding="utf-8") as f:
        statute_chunks = json.load(f)
        
    all_chunks = statute_chunks + all_judgment_chunks
    with open(OUTPUT_ALL_CHUNKS, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"\n[PHASE 11 COMPLETE] Unified corpus created with {len(all_chunks)} chunks:")
    print(f"  - Statutory Section Chunks: {len(statute_chunks)}")
    print(f"  - Precedent Semantic Chunks: {len(all_judgment_chunks)}")
    print(f"Saved to: {OUTPUT_ALL_CHUNKS}")

if __name__ == "__main__":
    main()
