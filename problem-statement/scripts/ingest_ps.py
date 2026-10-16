"""Universal Problem Statement (PS) Ingestion Helper.

Ingests PS files across multiple formats (PDF, Markdown, plain text, HTML, etc.)
or directories of PS documents into a standardized ps.txt with extraction diagnostics
saved in extraction.json.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Dict, List, Any

# Ensure sibling scripts can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_pdf import extract_pdf


def ingest_text_file(file_path: Path, out_dir: Path) -> Dict[str, Any]:
    file_path = file_path.resolve()
    out_dir = out_dir.resolve()
    text_path = out_dir / "ps.txt"
    report_path = out_dir / "extraction.json"
    if file_path in (text_path, report_path):
        raise ValueError("The output would replace the source file.")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    if not content.strip():
        raise ValueError("The input text file is empty.")

    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    lines = content.splitlines()
    words = len(content.split())
    chars = len(content)

    # Detect headings for quick outline navigation
    headings = []
    heading_pattern = re.compile(r"^(#{1,6}\s+.*|[A-Z0-9\.\s]{3,40}\n[-=]{3,})", re.MULTILINE)
    for line_idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            headings.append({"line": line_idx, "heading": stripped})

    report = {
        "source": str(file_path),
        "sha256": digest,
        "format": file_path.suffix.lower() or "text",
        "line_count": len(lines),
        "word_count": words,
        "character_count": chars,
        "method": "Direct text ingestion; UTF-8 preserved",
        "text_file": "ps.txt",
        "detected_headings": headings[:30],
        "pages_needing_visual_review": [],
        "coverage_note": (
            "Text ingested cleanly. Review embedded tables, formulas, or referenced links."
        ),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    text_path.write_text(content, encoding="utf-8")
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def ingest_directory(dir_path: Path, out_dir: Path) -> Dict[str, Any]:
    dir_path = dir_path.resolve()
    out_dir = out_dir.resolve()
    if dir_path == out_dir or out_dir in dir_path.parents:
        raise ValueError("Output directory cannot be inside or identical to the source directory.")

    supported_suffixes = {".pdf", ".md", ".txt", ".markdown", ".rst", ".html", ".htm"}
    files = sorted([p for p in dir_path.iterdir() if p.is_file() and p.suffix.lower() in supported_suffixes])
    if not files:
        raise ValueError(f"No supported problem statement files found in directory: {dir_path}")

    combined_chunks = []
    manifest = []
    total_words = 0
    total_chars = 0

    for file in files:
        if file.suffix.lower() == ".pdf":
            # Extract PDF to temporary memory
            import pymupdf
            with pymupdf.open(file) as doc:
                pdf_chunks = []
                for num, page in enumerate(doc, 1):
                    p_text = page.get_text("text", sort=True).rstrip()
                    pdf_chunks.append(f"--- [Page {num}/{doc.page_count}] ---\n{p_text}")
                file_text = "\n\n".join(pdf_chunks)
        else:
            file_text = file.read_text(encoding="utf-8", errors="replace")

        combined_chunks.append(f"==================== DOCUMENT: {file.name} ====================\n{file_text}\n")
        total_words += len(file_text.split())
        total_chars += len(file_text)
        manifest.append({
            "name": file.name,
            "path": str(file),
            "size_bytes": file.stat().st_size,
        })

    combined_text = "\n\n".join(combined_chunks)
    digest = hashlib.sha256(combined_text.encode("utf-8")).hexdigest()

    report = {
        "source": str(dir_path),
        "source_type": "directory",
        "sha256": digest,
        "format": "multi-document bundle",
        "file_count": len(files),
        "manifest": manifest,
        "word_count": total_words,
        "character_count": total_chars,
        "method": "Multi-document aggregation into unified ps.txt",
        "text_file": "ps.txt",
        "pages_needing_visual_review": [],
        "coverage_note": "Multi-file bundle aggregated. Inspect each document section as needed.",
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ps.txt").write_text(combined_text, encoding="utf-8")
    (out_dir / "extraction.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def ingest_ps(input_target: Path, out_dir: Path) -> Dict[str, Any]:
    input_target = input_target.resolve()
    if not input_target.exists():
        raise FileNotFoundError(f"Source target does not exist: {input_target}")

    if input_target.is_dir():
        return ingest_directory(input_target, out_dir)

    suffix = input_target.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf(input_target, out_dir)
    else:
        return ingest_text_file(input_target, out_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_target", type=Path, help="Path to PDF, text/markdown file, or folder of PS documents.")
    parser.add_argument("out_dir", type=Path, help="Target directory for ps.txt and extraction.json.")
    args = parser.parse_args()

    try:
        report = ingest_ps(args.input_target, args.out_dir)
    except ModuleNotFoundError as error:
        if error.name == "pymupdf":
            parser.exit(1, "PyMuPDF is required for PDF extraction. Install pymupdf or provide text/markdown.\n")
        raise
    except (OSError, ValueError, RuntimeError, FileNotFoundError) as error:
        parser.exit(1, f"PS ingestion failed: {error}\n")

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
