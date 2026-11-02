"""Unit tests for ingest_ps.py covering PDF, text/markdown, and directories."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import pymupdf

from ingest_ps import ingest_ps


class IngestPsTests(unittest.TestCase):
    def test_markdown_ingestion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "problem.md"
            source.write_text(
                "# Problem Title\n\n## Overview\nBuild an autonomous drone navigation agent.\n\n## Constraints\nMax 100ms latency.",
                encoding="utf-8",
            )
            out_dir = root / "output"
            report = ingest_ps(source, out_dir)

            ps_txt = (out_dir / "ps.txt").read_text(encoding="utf-8")
            extraction = json.loads((out_dir / "extraction.json").read_text(encoding="utf-8"))

            self.assertIn("# Problem Title", ps_txt)
            self.assertIn("autonomous drone navigation", ps_txt)
            self.assertEqual(report["format"], ".md")
            self.assertEqual(len(report["detected_headings"]), 3)
            self.assertEqual(extraction["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())

    def test_pdf_delegation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "problem.pdf"
            with pymupdf.open() as doc:
                doc.new_page().insert_text((72, 72), "Evaluation: Accuracy > 0.95")
                doc.save(source)

            out_dir = root / "output"
            report = ingest_ps(source, out_dir)

            self.assertEqual(report["page_count"], 1)
            ps_txt = (out_dir / "ps.txt").read_text(encoding="utf-8")
            self.assertIn("PDF PAGE 1 OF 1", ps_txt)
            self.assertIn("Accuracy > 0.95", ps_txt)

    def test_directory_bundle_ingestion(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ps_dir = root / "ps_bundle"
            ps_dir.mkdir()
            (ps_dir / "01_overview.md").write_text("# Overview\nChallenge details.", encoding="utf-8")
            (ps_dir / "02_rules.txt").write_text("Rule 1: No external APIs.", encoding="utf-8")

            out_dir = root / "output"
            report = ingest_ps(ps_dir, out_dir)

            ps_txt = (out_dir / "ps.txt").read_text(encoding="utf-8")
            self.assertIn("DOCUMENT: 01_overview.md", ps_txt)
            self.assertIn("DOCUMENT: 02_rules.txt", ps_txt)
            self.assertEqual(report["file_count"], 2)

    def test_empty_text_file_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "empty.txt"
            source.write_text("   ", encoding="utf-8")
            out_dir = root / "output"
            with self.assertRaises(ValueError):
                ingest_ps(source, out_dir)


if __name__ == "__main__":
    unittest.main()
