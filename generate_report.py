import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
METADATA_FILE = BASE_DIR / "judgment_metadata.json"
REPORT_FILE = Path("/Users/palakwadhwanii/.gemini/antigravity-ide/brain/39df3f78-7232-4630-b4e9-448715f805ac/judgment_metadata_enrichment_report.md")

def main():
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = [
        "# Step 2: Judgment Metadata Enrichment & Relevance Analysis Report",
        "",
        "> [!NOTE]",
        "> This report details the comprehensive metadata enrichment and relevance categorization performed on all **91 candidate judgments** across the 12 Family Law statutes from the Supreme Court of India (2023–2025).",
        "",
        "## 1. Executive Summary & Distribution",
        "",
        "### Relevance Tier Breakdown",
        "| Relevance Tier | Count | Description |",
        "| :--- | :--- | :--- |",
        "| **DIRECT** | 64 | Core substantive family law adjudication under one of the 12 target statutes (Divorce, Maintenance, Succession, Custody, Domestic Violence, Adoption). |",
        "| **RELATED** | 14 | Procedural, criminal, or evidentiary proceedings directly impacting matrimonial disputes (Section 498A IPC quashing, s.125 CrPC maintenance, Section 482 CrPC against DV orders, transit anticipatory bail). |",
        "| **MENTION_ONLY** | 5 | Passing statutory references or analogical citations in unrelated public law/civil disputes (e.g., Article 370, caste certificate verification, proof of age in motor accident claims). |",
        "| **NOT_RELEVANT** | 8 | Non-family law disputes where a family statute was cited incidentally in passing (e.g., land acquisition under the 2013 Act, judicial service promotions, criminal free speech). |",
        "| **TOTAL** | **91** | **Complete candidate dataset** |",
        "",
        "### Chronological Distribution",
        "- **2023 Judgments**: 27",
        "- **2024 Judgments**: 32",
        "- **2025 Judgments**: 32",
        "",
        "---",
        "",
        "## 2. Complete Catalog of 91 Enriched Judgments",
        "",
        "| # | Judgment ID | Case Name | Year | Sub-Case Type | Tier | Key Acts & Sections Invoked |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for i, d in enumerate(data):
        acts_strs = []
        for act, secs in d["acts_and_sections_invoked"].items():
            if secs:
                acts_strs.append(f"{act} ({', '.join(secs)})")
            else:
                acts_strs.append(act)
        acts_disp = "; ".join(acts_strs[:2])
        if len(acts_strs) > 2:
            acts_disp += f" (+{len(acts_strs)-2} more)"
        if not acts_disp:
            acts_disp = "None directly invoked"

        case_clean = d["case_name"].replace("|", "–")
        if len(case_clean) > 42:
            case_clean = case_clean[:39] + "..."

        jid = d["judgment_id"]
        tier = d["relevance_tier"]
        year = d["year"]
        stype = d["sub_case_type"]

        lines.append(f"| {i+1} | `{jid}` | {case_clean} | {year} | {stype} | **{tier}** | {acts_disp} |")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Successfully generated clean report with {len(data)} items to {REPORT_FILE}")

if __name__ == "__main__":
    main()
