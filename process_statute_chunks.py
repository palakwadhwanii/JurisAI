import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ACT_TEXTS_DIR = BASE_DIR / "act_texts"
SECTION_METADATA_FILE = BASE_DIR / "section_metadata.json"
ACT_METADATA_FILE = BASE_DIR / "act_metadata.json"
OUTPUT_STATUTE_CHUNKS = BASE_DIR / "chunks" / "statute_chunks.json"

def clean_raw_act_text(text):
    # Remove PDF page markers and headers
    t = re.sub(r"={3,}\s*PAGE\s+\d+\s*={3,}", "", text, flags=re.IGNORECASE)
    t = re.sub(r"(?m)^\s*IndiaCode\s*$", "", t, flags=re.IGNORECASE)
    t = re.sub(r"(?m)^\s*\d+\s*$", "", t)
    return t

def detect_statutory_constraints(sec_text):
    """
    Detect procedural and statutory constraints for the Constraint Hunter Agent:
    - Provisos and exceptions
    - Time limitations / cooling-off / thresholds
    - Statutory bars and disqualifications
    - Mandatory conditions precedent
    """
    constraints = []
    
    # 1. Provisos & Exceptions
    provisos = re.findall(r"(Provided(?:\s+further)?\s+that[^\.\n]+(?:\.|\n))", sec_text, re.IGNORECASE)
    for p in provisos[:3]:
        constraints.append({
            "constraint_type": "STATUTORY_PROVISO",
            "description": "Statutory exception or conditional qualification",
            "snippet": p.strip()[:200]
        })
        
    # 2. Time limitations / Waiting periods / Thresholds
    time_matches = re.findall(r"(?:within|period\s+of|after\s+the\s+expiry\s+of|not\s+less\s+than)\s+(\w+(?:\s+\w+)?\s+(?:days?|months?|years?))", sec_text, re.IGNORECASE)
    for tm in set(time_matches):
        constraints.append({
            "constraint_type": "TEMPORAL_LIMITATION",
            "description": f"Mandatory time threshold or limitation: {tm.strip()}",
            "snippet": tm.strip()
        })
        
    # 3. Statutory Bars & Disqualifications
    bars = re.findall(r"(shall\s+not\s+(?:be\s+entitled|lie|entertain|grant|be\s+deemed)|no\s+(?:petition|decree|suit|appeal|application)\s+shall\s+be[^\.\n]+)", sec_text, re.IGNORECASE)
    for b in bars[:3]:
        constraints.append({
            "constraint_type": "PROCEDURAL_BAR",
            "description": "Statutory bar or disqualification to relief",
            "snippet": b.strip()[:200]
        })
        
    # 4. Mandatory Conditions Precedent
    conds = re.findall(r"(condition[s]?\s+for\s+[^\.\n]+|unless\s+[^\.\n]+|subject\s+to\s+the\s+provisions[^\.\n]+)", sec_text, re.IGNORECASE)
    for c in conds[:2]:
        constraints.append({
            "constraint_type": "MANDATORY_CONDITION",
            "description": "Condition precedent required for relief",
            "snippet": c.strip()[:200]
        })
        
    return constraints

def process_act(act_info, raw_text):
    act_id = act_info["act_id"]
    act_name = act_info["act_name"]
    category = act_info.get("category", "Family Law")
    domain = act_info.get("domain", "Family Law")
    year = act_info.get("year", 0)
    
    cleaned = clean_raw_act_text(raw_text)
    
    # Locate where substantive body starts after enactment formula
    m_enact = re.search(r"enacted\b[^\n]*\bas\s+follows[:\s\u2010-\u2015\-–—―]*", cleaned, re.IGNORECASE)
    body = cleaned[m_enact.end():] if m_enact else cleaned
    
    expected_sections = act_info["sections"]
    sec_spans = []
    
    for s_info in expected_sections:
        s_num = s_info["section_number"]
        # Pattern matching section start: optional amendment number [digit, optional space, open bracket], section number, dot
        pat = rf"(?m)(?:^|[ \t]|\n)(?:\d+\s*\[)?{re.escape(s_num)}\.\s*"
        matches = list(re.finditer(pat, body))
        if matches:
            best_m = matches[0]
            # If multiple matches, check which has section title following it
            title_words = [w.lower() for w in s_info["section_title"].split() if len(w) > 3]
            for m in matches:
                after = body[m.end():m.end()+80].lower()
                if any(tw in after for tw in title_words):
                    best_m = m
                    break
            sec_spans.append({
                "section_number": s_num,
                "section_title": s_info["section_title"],
                "start": best_m.start()
            })
            
    sec_spans.sort(key=lambda x: x["start"])
    
    extracted_sections = []
    chunks = []
    
    for i, span in enumerate(sec_spans):
        start = span["start"]
        end = sec_spans[i + 1]["start"] if i + 1 < len(sec_spans) else len(body)
        raw_sec = body[start:end].strip()
        
        # Clean footnote definitions at bottom of section
        lines = raw_sec.splitlines()
        cleaned_lines = []
        for l in lines:
            if re.match(r"^\s*\d+\.\s+(Subs|Ins|Omitted|Repealed|The words|Certain words|This Act)\b", l, re.IGNORECASE):
                continue
            cleaned_lines.append(l)
        sec_text = "\n".join(cleaned_lines).strip()
        sec_text = re.sub(r"\n{3,}", "\n\n", sec_text)
        
        # Clean section header from text if it starts with section number
        s_num = span["section_number"]
        s_title = span["section_title"]
        
        extracted_sections.append({
            "section_number": s_num,
            "section_title": s_title,
            "section_text": sec_text
        })
        
        # Build statutory chunk for RAG
        context_header = f"[ACT: {act_name} | SECTION: {s_num} | TITLE: {s_title} | CATEGORY: {category}]"
        search_content = f"{context_header}\n\n{sec_text}"
        
        constraints = detect_statutory_constraints(sec_text)
        
        chunk = {
            "chunk_id": f"{act_id}_SEC_{s_num.replace('-', '_')}",
            "document_type": "statute",
            "act_id": act_id,
            "act_name": act_name,
            "year": year,
            "domain": domain,
            "category": category,
            "section_number": s_num,
            "section_title": s_title,
            "content": search_content,
            "context_header": context_header,
            "char_count": len(search_content),
            "token_estimate": len(search_content) // 4,
            "constraints_detected": constraints,
            "has_provisos": any(c["constraint_type"] == "STATUTORY_PROVISO" for c in constraints),
            "has_temporal_limits": any(c["constraint_type"] == "TEMPORAL_LIMITATION" for c in constraints),
            "has_bars": any(c["constraint_type"] == "PROCEDURAL_BAR" for c in constraints)
        }
        chunks.append(chunk)
        
    return extracted_sections, chunks

def main():
    print("Starting Phase 11: Statutory Document Processing...")
    
    with open(SECTION_METADATA_FILE, "r", encoding="utf-8") as f:
        sec_meta = json.load(f)
        
    updated_acts = []
    all_statute_chunks = []
    
    for act in sec_meta["acts"]:
        act_id = act["act_id"]
        fname = act["text_file"].strip()
        fp = ACT_TEXTS_DIR / fname
        if not fp.exists():
            found = list(ACT_TEXTS_DIR.glob(fname + "*"))
            if found:
                fp = found[0]
                
        raw_text = fp.read_text(encoding="utf-8", errors="ignore")
        extracted_sections, chunks = process_act(act, raw_text)
        
        act["sections"] = extracted_sections
        updated_acts.append(act)
        all_statute_chunks.extend(chunks)
        
        empty_count = sum(1 for s in extracted_sections if len(s["section_text"].strip()) == 0)
        print(f"  Processed {act_id} ({act['act_name']}): {len(extracted_sections)} sections extracted (Empty: {empty_count}), {len(chunks)} chunks created.")
        
    # 1. Update section_metadata.json with complete section texts
    sec_meta["acts"] = updated_acts
    with open(SECTION_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sec_meta, f, indent=2, ensure_ascii=False)
        
    # 2. Save statute chunks to chunks/statute_chunks.json
    OUTPUT_STATUTE_CHUNKS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_STATUTE_CHUNKS, "w", encoding="utf-8") as f:
        json.dump(all_statute_chunks, f, indent=2, ensure_ascii=False)
        
    print(f"\n[SUCCESS] Updated {SECTION_METADATA_FILE} with full section texts!")
    print(f"[SUCCESS] Saved {len(all_statute_chunks)} statute chunks to {OUTPUT_STATUTE_CHUNKS}")

if __name__ == "__main__":
    main()
