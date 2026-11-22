import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JUDGMENTS_BY_LAW_DIR = BASE_DIR / "judgments_by_law"
OUTPUT_FILE = BASE_DIR / "judgment_base_metadata.json"

TARGET_LAWS = {
    "Dissolution of Muslim Marriages Act 1939": "Dissolution of Muslim Marriages Act, 1939",
    "Divorce Act 1869": "Divorce Act, 1869",
    "Family Courts Act 1984": "Family Courts Act, 1984",
    "Guardians and Wards Act 1890": "Guardians and Wards Act, 1890",
    "Hindu Adoptions and Maintenance Act 1956": "Hindu Adoptions and Maintenance Act, 1956",
    "Hindu Marriage Act 1955": "Hindu Marriage Act, 1955",
    "Hindu Minority and Guardianship Act 1956": "Hindu Minority and Guardianship Act, 1956",
    "Hindu Succession Act 1956": "Hindu Succession Act, 1956",
    "Indian Christian Marriage Act 1872": "Indian Christian Marriage Act, 1872",
    "Prohibition of Child Marriage Act 2006": "Prohibition of Child Marriage Act, 2006",
    "Protection of Women from Domestic Violence Act 2005": "Protection of Women from Domestic Violence Act, 2005",
    "Special Marriage Act 1954": "Special Marriage Act, 1954",
}

def extract_case_details(text, filename):
    lines = [l.strip() for l in text.splitlines()[:70] if l.strip()]

    # 1. Year and Judgment ID
    m_year = re.match(r"(\d{4})_", filename)
    year = int(m_year.group(1)) if m_year else None
    judgment_id = Path(filename).stem

    # 2. SCR / INSC citation
    scr_citation = None
    insc_citation = None
    for l in lines[:15]:
        m = re.search(r"\[(\d{4})\]\s+(\d+\s+S\.C\.R\.\s+\d+)\s*:\s*(\d{4}\s+INSC\s+\d+)", l)
        if m:
            scr_citation = f"[{m.group(1)}] {m.group(2)}"
            insc_citation = m.group(3)
            break
        m2 = re.search(r"\[(\d{4})\]\s+(\d+\s+S\.C\.R\.\s+\d+)", l)
        if m2:
            scr_citation = f"[{m2.group(1)}] {m2.group(2)}"

    # 3. Case Name
    case_name = None
    # Check for IN RE
    for l in lines[:15]:
        if re.match(r"^IN RE\b", l, re.IGNORECASE):
            case_name = l
            break

    if not case_name:
        for i, l in enumerate(lines[:30]):
            if re.fullmatch(r"v\.?|versus|vs\.?", l, re.IGNORECASE):
                # Backtrack petitioner lines
                pet_parts = []
                j = i - 1
                while j >= 0:
                    cand = lines[j]
                    if re.match(r"^(CASE DETAILS|=====|\d+|[A-H]$|\[\d{4}\]|\*|SUPREME)", cand):
                        break
                    pet_parts.insert(0, cand)
                    j -= 1

                # Gather respondent lines
                resp_parts = []
                j = i + 1
                while j < len(lines):
                    cand = lines[j]
                    if cand.startswith("(") or re.match(r"^(JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER|\d{1,2}\s+[A-Za-z]+)", cand, re.IGNORECASE) or cand.startswith("["):
                        break
                    resp_parts.append(cand)
                    j += 1

                pet = " ".join(pet_parts).strip()
                resp = " ".join(resp_parts).strip()
                if pet and resp:
                    case_name = f"{pet} v. {resp}"
                break

    # 4. Appeal / Petition number
    appeal_no = None
    for l in lines[:30]:
        m = re.search(r"\((Civil Appeal|Criminal Appeal|Special Leave|Writ Petition|Transfer Petition|Suo Motu Writ Petition|Review Petition)[^\)]+\)", l, re.IGNORECASE)
        if m:
            appeal_no = m.group(0).strip("()")
            break

    # 5. Bench
    bench = []
    for l in lines[:35]:
        m = re.search(r"\[([A-Z\.\s,\*]+?(?:JJ|CJI)[\.]?)\]", l)
        if m:
            raw_bench = m.group(1)
            raw_bench = re.sub(r"\*|\bJJ\b|\bCJI\b|\band\b|,", "  ", raw_bench)
            bench = [name.strip() for name in re.split(r"\s{2,}", raw_bench) if len(name.strip()) > 2]
            break

    # 6. Date
    date_str = None
    date_pat = r"\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b|\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})\b"
    for l in lines[:30]:
        m = re.search(date_pat, l, re.IGNORECASE)
        if m:
            date_str = m.group(0)
            break

    # 7. Issue for Consideration from Headnotes
    issue_for_consideration = None
    m_issue = re.search(r"Issue[s]?\s+for\s+[Cc]onsideration[:\s]+(.*?)(?=(?:Headnotes|Held|\[\d+\]|[A-Z][a-z]+,\s+\d{4}\s*–|\n\s*\n\s*[A-Z]))", text, re.DOTALL)
    if m_issue:
        cleaned_issue = " ".join(m_issue.group(1).split())
        issue_for_consideration = cleaned_issue[:800]

    # 8. List of Acts from SCR (if present)
    scr_acts = []
    m_acts = re.search(r"List of Acts[:\s]+(.*?)(?=\n\s*(?:List of Keywords|Case Arising From|Headnotes|Held|\d+\s*\[\d{4}\]))", text, re.DOTALL | re.IGNORECASE)
    if m_acts:
        scr_acts = [a.strip() for a in m_acts.group(1).replace("\n", " ").split(";") if a.strip()]

    # 9. List of Keywords from SCR (if present)
    scr_keywords = []
    m_kw = re.search(r"List of Keywords[:\s]+(.*?)(?=\n\s*(?:Case Arising From|List of Acts|Headnotes|Held|\d+\s*\[\d{4}\]))", text, re.DOTALL | re.IGNORECASE)
    if m_kw:
        scr_keywords = [k.strip() for k in m_kw.group(1).replace("\n", " ").split(";") if k.strip()]

    return {
        "judgment_id": judgment_id,
        "case_name": case_name,
        "court": "Supreme Court of India",
        "year": year,
        "date": date_str,
        "appeal_number": appeal_no,
        "scr_citation": scr_citation,
        "insc_citation": insc_citation,
        "bench": bench,
        "issue_for_consideration": issue_for_consideration,
        "scr_acts": scr_acts,
        "scr_keywords": scr_keywords,
    }

def main():
    law_folders = [d for d in JUDGMENTS_BY_LAW_DIR.iterdir() if d.is_dir()]
    unique_files = {}

    for lf in sorted(law_folders):
        law_folder_name = lf.name
        standard_name = TARGET_LAWS.get(law_folder_name, law_folder_name)
        for f in lf.glob("*.txt"):
            if f.name not in unique_files:
                unique_files[f.name] = {
                    "path": f,
                    "matched_laws": [standard_name]
                }
            else:
                if standard_name not in unique_files[f.name]["matched_laws"]:
                    unique_files[f.name]["matched_laws"].append(standard_name)

    print(f"Total unique judgment files found: {len(unique_files)}")

    metadata_list = []
    for filename, info in sorted(unique_files.items()):
        text = info["path"].read_text(encoding="utf-8", errors="ignore")
        details = extract_case_details(text, filename)
        details["candidate_laws"] = sorted(info["matched_laws"])
        details["file_path"] = f"text/{filename}"
        metadata_list.append(details)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated clean base metadata for all {len(metadata_list)} judgments!")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
