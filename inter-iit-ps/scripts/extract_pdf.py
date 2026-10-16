"""Extract a PS PDF into page-marked UTF-8 text and review diagnostics."""

import argparse
import hashlib
import json
from pathlib import Path


def extract_pdf(pdf_path: Path, out_dir: Path) -> dict:
    import pymupdf

    pdf_path = pdf_path.resolve()
    out_dir = out_dir.resolve()
    text_path = out_dir / "ps.txt"
    report_path = out_dir / "extraction.json"
    if pdf_path in (text_path, report_path):
        raise ValueError("The output would replace the source PDF.")

    with pymupdf.open(pdf_path) as document:
        if not document.is_pdf:
            raise ValueError("The input is not a PDF.")
        if document.needs_pass:
            raise ValueError("The PDF is password-protected; provide an unlocked copy.")
        if not document.page_count:
            raise ValueError("The PDF has no pages.")

        chunks = []
        pages = []
        for number, page in enumerate(document, 1):
            text = page.get_text("text", sort=True)
            characters = len(text.strip())
            chunks.append(
                f"===== PDF PAGE {number} OF {document.page_count} =====\n"
                f"{text.rstrip()}\n"
            )
            pages.append({
                "page": number,
                "characters": characters,
                "words": len(text.split()),
                "embedded_images": len(page.get_images()),
                # Sparse text can be a blank/title page or a scan; inspect it visually.
                "needs_visual_review": characters < 40,
            })

    with pdf_path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha256").hexdigest()
    report = {
        "source_pdf": str(pdf_path),
        "sha256": digest,
        "page_count": len(pages),
        "method": "PyMuPDF embedded text, sorted by position; no OCR",
        "text_file": "ps.txt",
        "pages_needing_visual_review": [
            page["page"] for page in pages if page["needs_visual_review"]
        ],
        "pages": pages,
        "coverage_note": (
            "Inspect flagged pages and meaningful diagrams, tables, and equations. "
            "Text counts do not establish complete extraction."
        ),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    text_path.write_text("\n".join(chunks), encoding="utf-8")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args()
    try:
        report = extract_pdf(args.pdf, args.out_dir)
    except ModuleNotFoundError as error:
        if error.name != "pymupdf":
            raise
        parser.exit(1, "PyMuPDF is unavailable. Use another PDF extractor or install pymupdf.\n")
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"PDF extraction failed: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
