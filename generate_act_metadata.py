import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ACT_TEXTS_DIR = BASE_DIR / "act_texts"
ACT_METADATA_FILE = BASE_DIR / "act_metadata.json"
OUTPUT_FILE = BASE_DIR / "section_metadata.json"


# Sections that must be treated as the actual beginning
# of the statute for the problematic consolidated Acts.
ACTUAL_STARTS = {
    "HMA_1955": ("1", "Short title and extent"),
    "SMA_1954": ("1", "Short title"),
}


# Maximum valid section numbers for the 12 Acts.
# These are based on the statutory structure in the source texts.
MAX_SECTIONS = {
    "DMA_1939": 6,
    "DA_1869": 62,
    "FCA_1984": 23,
    "GWA_1890": 53,
    "HAMA_1956": 30,
    "HMA_1955": 30,
    "HMGA_1956": 13,
    "HSA_1956": 31,
    "ICMA_1872": 88,
    "PCMA_2006": 21,
    "PWDVA_2005": 37,
    "SMA_1954": 51,
}


def clean_text(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove PDF page markers
    text = re.sub(
        r"===== PAGE \d+ =====",
        "",
        text
    )

    # Remove IndiaCode markers
    text = re.sub(
        r"^\s*IndiaCode\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Remove standalone page numbers
    text = re.sub(
        r"^\s*\d+\s*$",
        "",
        text,
        flags=re.MULTILINE
    )

    # Join hyphenated line breaks
    text = re.sub(
        r"-\n(?=[a-z])",
        "",
        text
    )

    return text


def section_matches(text):
    """
    Match statutory section headings such as:

    1. Short title
    13A. Alternate relief
    21B. Special provision...
    """

    pattern = re.compile(
        r"(?m)^[ \t]*(\d+[A-Za-z]?)\.\s+(.+?)\s*$"
    )

    return list(pattern.finditer(text))


def is_amendment_entry(title):
    title = title.lower().strip()

    amendment_words = [
        "amendment) act",
        "amendment act",
        "foreign marriage act",
        "reorganisation act",
        "delegated legislation provisions",
        "personal laws (amendment)",
    ]

    return any(
        word in title
        for word in amendment_words
    )


def is_bad_entry(section_number, title):
    """
    Reject obvious TOC/amendment/footnote noise.
    """

    title_lower = title.lower().strip()

    # Amendment list
    if is_amendment_entry(title):
        return True

    # Footnote / amendment note
    bad_starts = [
        "subs. by",
        "subs by",
        "ins. by",
        "ins by",
        "omitted by",
        "repealed by",
        "the petition of",
    ]

    if title_lower.startswith(
        tuple(bad_starts)
    ):
        return True

    return False


def extract_sections(act, raw_text):

    act_id = act["act_id"]

    text = clean_text(raw_text)

    matches = section_matches(text)

    # ---------------------------------------------------------
    # STEP 1: Find candidate Section 1
    # ---------------------------------------------------------

    candidates = []

    for match in matches:

        number = match.group(1)
        title = match.group(2).strip()

        if number != "1":
            continue

        if is_bad_entry(number, title):
            continue

        candidates.append(match)

    # ---------------------------------------------------------
    # STEP 2: Pick actual Section 1
    # ---------------------------------------------------------

    actual_start = None

    expected_title = None

    if act_id in ACTUAL_STARTS:

        expected_number, expected_title = ACTUAL_STARTS[act_id]

        for match in candidates:

            title = match.group(2).strip().lower()

            if (
                expected_title.lower()
                in title
            ):
                actual_start = match.start()
                break

    # For all other Acts, use the first valid Section 1.
    if actual_start is None:

        if candidates:
            actual_start = candidates[0].start()

    if actual_start is None:

        print(
            "  ERROR: Could not find actual Section 1"
        )

        return []

    # Only process the statutory body
    body = text[actual_start:]

    matches = section_matches(body)

    sections = []

    max_section = MAX_SECTIONS.get(
        act_id,
        500
    )

    for i, match in enumerate(matches):

        section_number = match.group(1)
        section_title = match.group(2).strip()

        numeric_match = re.match(
            r"(\d+)",
            section_number
        )

        if not numeric_match:
            continue

        numeric = int(
            numeric_match.group(1)
        )

        # -----------------------------------------------------
        # Reject impossible sections
        # -----------------------------------------------------

        if numeric > max_section:
            continue

        if is_bad_entry(
            section_number,
            section_title
        ):
            continue

        # -----------------------------------------------------
        # HSA special case:
        # 6B and 6C are amendment-style artifacts
        # appearing after Section 31 in this source extraction.
        # -----------------------------------------------------

        if (
            act_id == "HSA_1956"
            and section_number in ["6B", "6C"]
        ):
            continue

        # -----------------------------------------------------
        # Find end of section
        # -----------------------------------------------------

        section_start = match.end()

        section_end = len(body)

        for next_match in matches[i + 1:]:

            next_number = next_match.group(1)

            next_numeric_match = re.match(
                r"(\d+)",
                next_number
            )

            if not next_numeric_match:
                continue

            next_numeric = int(
                next_numeric_match.group(1)
            )

            if next_numeric <= max_section:
                section_end = next_match.start()
                break

        section_text = body[
            section_start:section_end
        ].strip()

        # Normalize whitespace only.
        # Legal wording itself is preserved.
        section_text = re.sub(
            r"\n{3,}",
            "\n\n",
            section_text
        )

        section_text = re.sub(
            r"[ \t]+",
            " ",
            section_text
        )

        # Avoid duplicates
        if any(
            s["section_number"] == section_number
            for s in sections
        ):
            continue

        sections.append({
            "section_number": section_number,
            "section_title": section_title,
            "section_text": section_text
        })

    return sections


def main():

    print()
    print("=" * 50)
    print("        JURISAI SECTION METADATA V5")
    print("=" * 50)
    print()

    with open(
        ACT_METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        metadata = json.load(f)

    acts = metadata["acts"]

    output = []
    total = 0

    for act in acts:

        act_name = act["act_name"]
        filename = act["text_file"]

        print(
            f"Processing: {act_name}"
        )

        file_path = (
            ACT_TEXTS_DIR / filename
        )

        if not file_path.exists():

            print(
                f"  ERROR: {filename} not found"
            )

            output.append({
                **act,
                "sections": []
            })

            continue

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:
            raw_text = f.read()

        sections = extract_sections(
            act,
            raw_text
        )

        print(
            f"  Sections found: {len(sections)}"
        )

        total += len(sections)

        output.append({
            **act,
            "sections": sections
        })

    result = {
        "acts": output
    }

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print("=" * 50)
    print("DONE")
    print("=" * 50)
    print()
    print("SUMMARY")
    print()

    for act in output:

        print(
            f"{act['short_name']}: "
            f"{len(act['sections'])}"
        )

    print()
    print(
        f"TOTAL: {total}"
    )


if __name__ == "__main__":
    main()