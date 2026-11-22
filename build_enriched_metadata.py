import json
from pathlib import Path
from enrichment.enrich_2023 import DATA_2023
from enrichment.enrich_2024 import DATA_2024
from enrichment.enrich_2025 import DATA_2025

BASE_DIR = Path(__file__).resolve().parent
BASE_METADATA_FILE = BASE_DIR / "judgment_base_metadata.json"
OUTPUT_METADATA_FILE = BASE_DIR / "judgment_metadata.json"
OUTPUT_ENRICHED_FILE = BASE_DIR / "judgment_enriched_metadata.json"

REQUIRED_FIELDS = [
    "acts_and_sections_invoked",
    "facts_summary",
    "legal_issues",
    "decision_holding",
    "legal_principles",
    "sub_case_type",
    "relevance_tier",
    "relevance_reason",
]

def main():
    with open(BASE_METADATA_FILE, "r", encoding="utf-8") as f:
        base_judgments = json.load(f)

    all_enriched = {}
    all_enriched.update(DATA_2023)
    all_enriched.update(DATA_2024)
    all_enriched.update(DATA_2025)

    enriched_judgments = []

    for item in base_judgments:
        jid = item["judgment_id"]
        if jid not in all_enriched:
            raise ValueError(f"Missing enriched data for judgment {jid}")

        enrichment = all_enriched[jid]

        # Verify all required fields
        for field in REQUIRED_FIELDS:
            if field not in enrichment:
                raise ValueError(f"Missing field '{field}' in judgment {jid}")
            if enrichment[field] is None:
                raise ValueError(f"Field '{field}' is None in judgment {jid}")

        merged = {
            "judgment_id": item.get("judgment_id"),
            "case_name": item.get("case_name"),
            "court": item.get("court", "Supreme Court of India"),
            "year": item.get("year"),
            "date": item.get("date"),
            "appeal_number": item.get("appeal_number"),
            "scr_citation": item.get("scr_citation"),
            "insc_citation": item.get("insc_citation"),
            "bench": item.get("bench", []),
            "candidate_laws": item.get("candidate_laws", []),
            "acts_and_sections_invoked": enrichment["acts_and_sections_invoked"],
            "facts_summary": enrichment["facts_summary"],
            "legal_issues": enrichment["legal_issues"],
            "decision_holding": enrichment["decision_holding"],
            "legal_principles": enrichment["legal_principles"],
            "sub_case_type": enrichment["sub_case_type"],
            "relevance_tier": enrichment["relevance_tier"],
            "relevance_reason": enrichment["relevance_reason"],
            "file_path": item.get("file_path"),
        }

        enriched_judgments.append(merged)

    # Save to both judgment_metadata.json and judgment_enriched_metadata.json
    with open(OUTPUT_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_judgments, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_ENRICHED_FILE, "w", encoding="utf-8") as f:
        json.dump(enriched_judgments, f, indent=2, ensure_ascii=False)

    print(f"Successfully processed and validated all {len(enriched_judgments)} judgments!")
    print(f"Updated main metadata: {OUTPUT_METADATA_FILE}")
    print(f"Saved enriched metadata: {OUTPUT_ENRICHED_FILE}")

    # Summary statistics
    tiers = {}
    subtypes = {}
    for ej in enriched_judgments:
        t = ej["relevance_tier"]
        tiers[t] = tiers.get(t, 0) + 1
        st = ej["sub_case_type"].split("/")[0].strip()
        subtypes[st] = subtypes.get(st, 0) + 1

    print("\n--- RELEVANCE TIER DISTRIBUTION ---")
    for t, c in sorted(tiers.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    print("\n--- SUB-CASE TYPE DISTRIBUTION ---")
    for st, c in sorted(subtypes.items(), key=lambda x: -x[1]):
        print(f"  {st}: {c}")

if __name__ == "__main__":
    main()
