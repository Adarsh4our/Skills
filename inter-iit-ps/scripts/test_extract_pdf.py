"""Exercise extraction against temporary PDFs; no network or user PDFs required."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import pymupdf

from extract_pdf import extract_pdf


class ExtractPdfTests(unittest.TestCase):
    def test_multipage_text_and_source_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source with spaces.pdf"
            with pymupdf.open() as document:
                document.new_page().insert_text(
                    (72, 72), "Goal: classify observations from multiple sensors.\nBudget: 100."
                )
                document.new_page().insert_text(
                    (72, 72), "Evaluation: recall on the supplied test data.\nDeliverable: code and report."
                )
                document.save(source)
            original = source.read_bytes()
            report = extract_pdf(source, root / "output")
            text = (root / "output" / "ps.txt").read_text(encoding="utf-8")
            saved = json.loads((root / "output" / "extraction.json").read_text(encoding="utf-8"))
            self.assertIn("PDF PAGE 1 OF 2", text)
            self.assertIn("PDF PAGE 2 OF 2", text)
            self.assertLess(text.index("Goal:"), text.index("Evaluation:"))
            self.assertIn("Budget: 100.", text)
            self.assertEqual(report["page_count"], 2)
            self.assertEqual(report["pages_needing_visual_review"], [])
            self.assertEqual(saved["sha256"], hashlib.sha256(original).hexdigest())
            self.assertEqual(source.read_bytes(), original)

    def test_image_only_page_is_flagged_and_retained(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "scan.pdf"
            with pymupdf.open() as document:
                page = document.new_page()
                image = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.Rect(0, 0, 20, 20), 0)
                image.clear_with(255)
                page.insert_image(pymupdf.Rect(72, 72, 172, 172), pixmap=image)
                document.save(source)
            report = extract_pdf(source, root / "output")
            self.assertEqual(report["pages_needing_visual_review"], [1])
            self.assertEqual(report["pages"][0]["embedded_images"], 1)
            self.assertIn("PDF PAGE 1 OF 1", (root / "output" / "ps.txt").read_text())

    def test_locked_pdf_fails_without_partial_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "locked.pdf"
            with pymupdf.open() as document:
                document.new_page().insert_text((72, 72), "Private test fixture")
                document.save(
                    source,
                    encryption=pymupdf.PDF_ENCRYPT_AES_256,
                    owner_pw="test-owner",
                    user_pw="test-user",
                )
            with self.assertRaisesRegex(ValueError, "password-protected"):
                extract_pdf(source, root / "output")
            self.assertFalse((root / "output").exists())

    def test_non_pdf_input_fails_without_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "ordinary.txt"
            source.write_text("This is not a PDF.", encoding="utf-8")
            with self.assertRaises((ValueError, RuntimeError)):
                extract_pdf(source, root / "output")
            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
