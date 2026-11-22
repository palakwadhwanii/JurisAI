import re
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

JUDGMENTS_DIR = BASE_DIR / "text"
OUTPUT_FILE = BASE_DIR / "judgment_metadata.json"


def extract_year(filename):
    """
    Example:
    2023_INSC_985.txt -> 2023
    """

    match = re.match(
        r"(\d{4})_",
        filename
    )

    if match:
        return int(match.group(1))

    return None


def extract_judgment_id(filename):

    return Path(filename).stem


def extract_case_name(text):

    patterns = [
        r"(.+?)\s+VERSUS\s+(.+?)",
        r"(.+?)\s+Vs\.\s+(.+?)",
        r"(.+?)\s+v\.\s+(.+?)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            petitioner = match.group(1).strip()
            respondent = match.group(2).strip()

            return (
                petitioner +
                " v. " +
                respondent
            )

    return None


def extract_date(text):

    patterns = [
        r"Date of Judgment[:\s]+([0-9./-]+)",
        r"Judgment Date[:\s]+([0-9./-]+)",
        r"DATED[:\s]+([0-9./-]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return None


def extract_bench(text):

    judges = []

    patterns = [
        r"HON'?BLE\s+MR\.?\s+JUSTICE\s+([A-Z][A-Za-z .]+)",
        r"HON'?BLE\s+MS\.?\s+JUSTICE\s+([A-Z][A-Za-z .]+)",
        r"HON'?BLE\s+MRS\.?\s+JUSTICE\s+([A-Z][A-Za-z .]+)"
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for judge in matches:

            judge = judge.strip()

            if judge not in judges:
                judges.append(judge)

    return judges


def create_metadata(file_path):

    filename = file_path.name

    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    metadata = {

        "judgment_id":
            extract_judgment_id(filename),

        "case_name":
            extract_case_name(text),

        "court":
            "Supreme Court of India",

        "year":
            extract_year(filename),

        "date":
            extract_date(text),

        "bench":
            extract_bench(text),

        "acts": [],

        "sections": [],

        "legal_issues": [],

        "case_type":
            "Family Law",

        "relevance":
            None,

        "keywords": [],

        "source":
            "Supreme Court of India",

        "file_path":
            str(file_path.relative_to(BASE_DIR))
    }

    return metadata


def main():

    judgments = []

    files = sorted(
        JUDGMENTS_DIR.glob("*.txt")
    )[:100]

    print(
        f"Found {len(files)} judgments."
    )

    for i, file_path in enumerate(files):

        metadata = create_metadata(
            file_path
        )

        judgments.append(metadata)

        if (i + 1) % 100 == 0:

            print(
                f"Processed {i + 1}"
            )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            judgments,
            f,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        f"Saved metadata to:"
    )
    print(
        OUTPUT_FILE
    )


if __name__ == "__main__":
    main()