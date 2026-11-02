---
name: markdown_handbook_formatter
description: >
  Formats raw, double-spaced study handbooks and slide-style Markdown files into
  clean, structured Markdown. Triggers when the user asks to "format", "clean up",
  or "fix" a .md file that looks like a raw export or study guide with excessive
  blank lines, plain-text flowcharts (using ↓ arrows), ASCII diagrams, tab-separated
  tables, and unstructured headings.
---

# Markdown Handbook Formatter Skill

## When to Use This Skill

Trigger this skill when the user provides a `.md` file that:
- Has excessive double/triple blank lines between every line
- Uses `↓` arrows to show flowcharts or execution sequences
- Has ASCII box diagrams (`+------+`, `│`, `├──`, etc.)
- Has tab-separated tables
- Has assembly code snippets mixed with text
- Lacks proper heading hierarchy (`#`, `##`, `###`)

## How to Execute

1. Locate the formatter script at `scripts/formatter.py` relative to this skill directory.
2. Run it with Python using the input file path:

```
python scripts/formatter.py "<input_file.md>" "<output_file.md>"
```

Or to overwrite in-place (with automatic backup):

```
python scripts/formatter.py "<input_file.md>"
```

This will:
- Save a backup to `<input_file>.bak`
- Overwrite the original with the formatted version

3. After running, verify the output by viewing a sample of lines and confirming:
   - Headings are properly structured (`##` for chapters, `###` for sections)
   - Flowcharts render as Mermaid diagrams
   - Tables are formatted as pipe-separated Markdown tables
   - Code blocks use proper fencing (` ```assembly `, ` ```text `)
   - All original words are preserved (the script will print a verification summary)

## Key Formatting Rules Applied

| Element | Original Format | Formatted Output |
| :--- | :--- | :--- |
| Chapter title | `Chapter 3 — Title` | `## Chapter 3 — Title` |
| Section title | `The Fundamental Problem` (standalone) | `### The Fundamental Problem` |
| Flowchart | `Item A`, `↓`, `Item B`, `↓`, `Item C` | Mermaid `flowchart TD` block |
| ASCII diagram | `+-----+`, `│ text │` | ` ```text ` block |
| Tab table | `Col1\tCol2\n...` | Markdown pipe table |
| Assembly | `MOV R1, R2` standalone line | ` ```assembly ` block |
| Lists | Scattered single-word lines under a heading | `- item` list |
| Q&A blocks | `Q1`, then question, then `Expected Answer` | `### Q1: Question text` + `**Expected Answer:**` |
| Solutions | `Solution 1` heading | `### Solution 1` |

## Notes & Limitations

- The formatter uses **heuristic Title Case detection** for subheadings. Short lines (< 40 chars) that are Title Case and don't end in punctuation are promoted to `###`. If a heading is missed or a non-heading is promoted, you can manually fix it after.
- The **diagram expansion pass** tries to group adjacent short lines into diagrams. Occasionally a very short text sentence adjacent to a diagram may get absorbed — review the output for correctness.
- The script **never loses content**: a word-level verification runs at the end and prints a warning if any words from the original are missing.
