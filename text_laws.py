import fitz
from pathlib import Path

# Folder containing your PDFs
laws_folder = Path("laws")

# Process every PDF
for pdf_file in laws_folder.glob("*.pdf"):

    print(f"Processing: {pdf_file.name}")

    doc = fitz.open(pdf_file)

    text = []

    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text()

        text.append(
            f"\n\n===== PAGE {page_number} =====\n\n"
        )
        text.append(page_text)

    # Create TXT file with the same name
    txt_file = pdf_file.with_suffix(".txt")

    txt_file.write_text(
        "".join(text),
        encoding="utf-8"
    )

    doc.close()

    print(f"✓ Created: {txt_file.name}")

print("\nAll laws converted successfully!")