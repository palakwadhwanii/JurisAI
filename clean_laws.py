import re
from pathlib import Path


# Folder containing the extracted TXT files
input_folder = Path("text_laws")

# Folder where cleaned files will be saved
output_folder = Path("cleaned_laws")

output_folder.mkdir(exist_ok=True)


def clean_text(text):

    # --------------------------------------------------
    # 1. Remove page markers
    # Example:
    # ===== PAGE 1 =====
    # --------------------------------------------------

    text = re.sub(
        r'={3,}\s*PAGE\s+\d+\s*={3,}',
        '',
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # 2. Remove standalone page numbers
    # Example:
    # 1
    # 2
    # 15
    # --------------------------------------------------

    text = re.sub(
        r'(?m)^\s*\d+\s*$',
        '',
        text
    )

    # --------------------------------------------------
    # 3. Remove IndiaCode
    # --------------------------------------------------

    text = re.sub(
        r'(?m)^\s*IndiaCode\s*$',
        '',
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # 4. Fix words split across lines
    #
    # Example:
    #
    # jurisdic-
    # tion
    #
    # becomes:
    #
    # jurisdiction
    # --------------------------------------------------

    text = re.sub(
        r'(\w)-\s*\n\s*(\w)',
        r'\1\2',
        text
    )

    # --------------------------------------------------
    # 5. Replace normal line breaks with spaces
    #
    # Example:
    #
    # This Act shall be read subject to
    # every enactment...
    #
    # becomes:
    #
    # This Act shall be read subject to every enactment...
    # --------------------------------------------------

    text = re.sub(
        r'(?<!\n)\n(?!\n)',
        ' ',
        text
    )

    # --------------------------------------------------
    # 6. Remove excessive spaces
    # --------------------------------------------------

    text = re.sub(
        r'[ \t]+',
        ' ',
        text
    )

    # --------------------------------------------------
    # 7. Clean excessive blank lines
    # --------------------------------------------------

    text = re.sub(
        r'\n\s*\n\s*\n+',
        '\n\n',
        text
    )

    # --------------------------------------------------
    # 8. Remove spaces at beginning/end of lines
    # --------------------------------------------------

    text = '\n'.join(
        line.strip()
        for line in text.splitlines()
    )

    # --------------------------------------------------
    # 9. Final cleanup of excessive blank lines
    # --------------------------------------------------

    text = re.sub(
        r'\n{3,}',
        '\n\n',
        text
    )

    return text.strip()


# ------------------------------------------------------
# Process every TXT file
# ------------------------------------------------------

txt_files = list(input_folder.glob("*.txt"))

print(f"Found {len(txt_files)} text files.\n")


for txt_file in txt_files:

    print(f"Cleaning: {txt_file.name}")

    # Read original text
    text = txt_file.read_text(
        encoding="utf-8",
        errors="replace"
    )

    # Clean the text
    cleaned = clean_text(text)

    # Save cleaned file
    output_file = output_folder / txt_file.name

    output_file.write_text(
        cleaned,
        encoding="utf-8"
    )

    print(f"✓ Saved: {output_file}")


print("\nAll files cleaned successfully!")