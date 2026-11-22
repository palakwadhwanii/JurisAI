import re
import shutil
from pathlib import Path


# ============================================================
# SETTINGS
# ============================================================

# Folder containing ALL your mixed judgment TXT files
input_folder = Path("text")

# Folder where judgments will be organized
output_folder = Path("judgments_by_law")

output_folder.mkdir(exist_ok=True)


# ============================================================
# THE 12 LAWS
# ============================================================

laws = {
    "Dissolution of Muslim Marriages Act 1939": [
        "dissolution of muslim marriages act, 1939",
        "dissolution of muslim marriages act",
    ],

    "Divorce Act 1869": [
        "the divorce act, 1869",
        "divorce act, 1869",
    ],

    "Family Courts Act 1984": [
        "the family courts act, 1984",
        "family courts act, 1984",
    ],

    "Guardians and Wards Act 1890": [
        "the guardians and wards act, 1890",
        "guardians and wards act, 1890",
    ],

    "Hindu Adoptions and Maintenance Act 1956": [
        "the hindu adoptions and maintenance act, 1956",
        "hindu adoptions and maintenance act, 1956",
    ],

    "Hindu Marriage Act 1955": [
        "the hindu marriage act, 1955",
        "hindu marriage act, 1955",
    ],

    "Hindu Minority and Guardianship Act 1956": [
        "the hindu minority and guardianship act, 1956",
        "hindu minority and guardianship act, 1956",
    ],

    "Hindu Succession Act 1956": [
        "the hindu succession act, 1956",
        "hindu succession act, 1956",
    ],

    "Indian Christian Marriage Act 1872": [
        "the indian christian marriage act, 1872",
        "indian christian marriage act, 1872",
    ],

    "Prohibition of Child Marriage Act 2006": [
        "the prohibition of child marriage act, 2006",
        "prohibition of child marriage act, 2006",
    ],

    "Protection of Women from Domestic Violence Act 2005": [
        "the protection of women from domestic violence act, 2005",
        "protection of women from domestic violence act, 2005",
    ],

    "Special Marriage Act 1954": [
        "the special marriage act, 1954",
        "special marriage act, 1954",
    ],
}


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize(text):
    """
    Makes PDF-extracted text easier to search.

    Example:

    "Hindu Marriage Act,\n1955"

    becomes:

    "hindu marriage act, 1955"
    """

    text = text.lower()

    # Replace all whitespace/newlines with one space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# PREPARE SEARCH TERMS
# ============================================================

normalized_laws = {}

for law_name, patterns in laws.items():

    normalized_laws[law_name] = [
        normalize(pattern)
        for pattern in patterns
    ]


# ============================================================
# FIND ALL TXT FILES
# ============================================================

txt_files = list(input_folder.glob("*.txt"))

print("=" * 70)
print(f"Found {len(txt_files)} TXT files")
print("=" * 70)
print()


# Keep track of results
results = {law: [] for law in laws}

total_processed = 0


# ============================================================
# SEARCH EVERY JUDGMENT
# ============================================================

for txt_file in txt_files:

    total_processed += 1

    try:
        original_text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    except Exception as e:

        print(f"ERROR reading {txt_file.name}: {e}")
        continue


    # Normalize for searching
    searchable_text = normalize(original_text)


    matched_laws = []


    # Check against all 12 laws
    for law_name, patterns in normalized_laws.items():

        found = False

        for pattern in patterns:

            if pattern in searchable_text:
                found = True
                break

        if found:
            matched_laws.append(law_name)


    # --------------------------------------------------------
    # If this judgment mentions at least one target law
    # --------------------------------------------------------

    if matched_laws:

        print(
            f"FOUND: {txt_file.name}"
        )

        print(
            f"       Laws: {', '.join(matched_laws)}"
        )

        print()


        # ----------------------------------------------------
        # Copy judgment into EVERY relevant law folder
        # ----------------------------------------------------

        for law_name in matched_laws:

            law_folder = output_folder / law_name

            law_folder.mkdir(
                parents=True,
                exist_ok=True
            )


            destination = law_folder / txt_file.name


            shutil.copy2(
                txt_file,
                destination
            )


            results[law_name].append(
                txt_file.name
            )


print()
print("=" * 70)
print("SEARCH COMPLETE")
print("=" * 70)

print()

for law_name, files in results.items():

    print(
        f"{law_name}: {len(files)} judgments"
    )


print()
print(f"Processed: {total_processed} files")
print()
print(f"Output folder: {output_folder.resolve()}")