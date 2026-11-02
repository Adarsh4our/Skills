#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown Handbook Formatter
============================
Formats raw double-spaced study handbooks and slide-style Markdown files into
clean, structured Markdown with proper headings, Mermaid flowcharts, ASCII
diagram code blocks, formatted tables, and assembly code blocks.

Usage:
    python formatter.py <input_file.md>
        → Backs up original to <input_file>.bak and overwrites in place.

    python formatter.py <input_file.md> <output_file.md>
        → Writes formatted content to output file. Original is unchanged.
"""

import re
import sys
import shutil
import os

# Ensure stdout can handle UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINOR_WORDS = {
    "a", "an", "the", "and", "but", "or", "for", "nor", "on", "in", "at", "to",
    "by", "with", "of", "vs", "from", "into", "onto", "under", "over", "above",
    "below", "through", "during", "before", "after", "about", "against",
    "between", "among", "throughout"
}


def is_title_case(s: str) -> bool:
    """Return True if the string looks like a Title Case heading."""
    s = s.strip().strip('*_`"\'')
    if s.isupper() and len(s) > 1:
        return True
    words = re.split(r'[\s\-—]+', s)
    if not words or not words[0]:
        return False
    for idx, w in enumerate(words):
        w_clean = re.sub(r'^\W+|\W+$', '', w)
        if not w_clean:
            continue
        if w_clean[0].isalpha():
            if w_clean.lower() in MINOR_WORDS and idx > 0:
                continue
            if not w_clean[0].isupper():
                return False
    return True


# ---------------------------------------------------------------------------
# Line Classifier
# ---------------------------------------------------------------------------

class LineClassifier:

    @staticmethod
    def is_table(line: str) -> bool:
        return '\t' in line

    @staticmethod
    def is_diagram_line(line: str) -> bool:
        s = line.strip()
        if not s:
            return False
        if any(c in "│├└─▼▲◀▶┌┐┬┴┼├┤" for c in s):
            return True
        if s in ('↓', '▼'):
            return True
        if re.match(r'^\s*[\+\-\|\=\#]{3,}\s*$', s):
            return True
        if s.startswith('|') and s.endswith('|'):
            return True
        if '├──' in s or '└──' in s:
            return True
        return False

    @staticmethod
    def is_main_heading(line: str) -> bool:
        s = line.strip()
        if re.match(r'^(Chapter|Module|Section)\s+[\d\.]+', s, re.IGNORECASE):
            return True
        if s in ("MODULE 0.5 HANDBOOK", "COVER PAGE"):
            return True
        if re.match(r'^Module\s+[\d\.]+\s*[—–-]', s):
            return True
        return False

    @staticmethod
    def is_explicit_subheading(line: str) -> bool:
        s = line.strip()
        if re.match(r'^Q\d+$', s):
            return True
        if re.match(r'^(Solution|Exercise|Path|Misconception|Generation|Level)\s+\d+', s, re.IGNORECASE):
            return True
        if s == "Expected Answer":
            return True
        if re.match(r'^Step\s+\d+', s, re.IGNORECASE):
            return True
        return False

    @staticmethod
    def is_sub_heading_candidate(line: str) -> bool:
        s = line.strip()
        if not s:
            return False
        if LineClassifier.is_explicit_subheading(line):
            return True
        if len(s) < 50 and not s.endswith(('.', '?', '!', ':', ',')):
            if is_title_case(s):
                exclusions = {
                    "Compiler", "Assembler", "Linker", "Loader", "Registers",
                    "Program Counter", "RAM", "Google", "Meta", "Microsoft",
                    "Amazon", "NVIDIA", "Jane Street", "HRT", "Citadel",
                    "Cloudflare", "User Mode", "Kernel Mode", "CPU",
                    "Operating System", "YES", "NO", "Yes", "No", "Why?", "Problem"
                }
                if s not in exclusions:
                    if not re.match(
                        r'^(MOV|ADD|SYSCALL|PUSH|POP|SUB|MUL|DIV|CMP|JMP|JE|'
                        r'JNE|JZ|JNZ|CALL|RET|IRET|SYSRET)\b', s
                    ):
                        return True
        return False

    @staticmethod
    def is_asm(line: str) -> bool:
        s = line.strip()
        if re.match(
            r'^\s*(MOV|ADD|SYSCALL|PUSH|POP|SUB|MUL|DIV|CMP|JMP|JE|JNE|JZ|'
            r'JNZ|CALL|RET|IRET|SYSRET|NEXT INSTRUCTION|RETURN\\_FROM\\_SYSCALL)\b',
            s, re.IGNORECASE
        ):
            return True
        if re.match(
            r'^\s*(RAX|RBX|RCX|RDX|RSI|RDI|RSP|RBP|RIP|R1|R2|R3|R4|'
            r'Mode Bit|Program Counter|Flags)\s*=', s
        ):
            return True
        return False


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def _merge_adjacent_blocks(blocks):
    """Merge adjacent FLOWCHART + DIAGRAM blocks into a single DIAGRAM."""
    merged = []
    i = 0
    n = len(blocks)
    while i < n:
        btype, bcontent = blocks[i]
        if btype == 'FLOWCHART' and i + 1 < n and blocks[i + 1][0] == 'DIAGRAM':
            items = bcontent
            diag = blocks[i + 1][1]
            combined = []
            for idx, item in enumerate(items):
                combined.append(item)
                if idx < len(items) - 1:
                    combined.append("  ↓")
            combined.extend(diag)
            merged.append(('DIAGRAM', combined))
            i += 2
            continue
        if btype == 'DIAGRAM' and i + 1 < n and blocks[i + 1][0] == 'FLOWCHART':
            diag = bcontent
            items = blocks[i + 1][1]
            combined = list(diag)
            for idx, item in enumerate(items):
                combined.append(item)
                if idx < len(items) - 1:
                    combined.append("  ↓")
            merged.append(('DIAGRAM', combined))
            i += 2
            continue
        merged.append((btype, bcontent))
        i += 1
    return merged


def parse_document(file_path: str):
    """Parse a raw double-spaced handbook .md file into structured blocks."""
    with open(file_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # Strip empty lines; keep all non-empty lines
    non_empty = [line.rstrip() for line in raw_lines if line.strip()]
    n = len(non_empty)

    # === Pass 1: Flag diagram lines ===
    is_diag = [LineClassifier.is_diagram_line(line) for line in non_empty]

    # Fill single-line gaps between two diagram lines
    for idx in range(1, n - 1):
        if not is_diag[idx] and is_diag[idx - 1] and is_diag[idx + 1]:
            is_diag[idx] = True

    # Expand diagrams to include adjacent short / indented lines
    # (skip expansion next to bare '↓' lines to avoid contaminating flowcharts)
    for idx in range(n):
        if is_diag[idx]:
            continue
        left_diag = idx > 0 and is_diag[idx - 1] and non_empty[idx - 1].strip() != '↓'
        right_diag = idx + 1 < n and is_diag[idx + 1] and non_empty[idx + 1].strip() != '↓'
        if left_diag or right_diag:
            s = non_empty[idx].strip()
            is_indented = non_empty[idx].startswith((' ', '\t', '&#x20;', '&nbsp;'))
            if (len(s) < 25 or is_indented) and not LineClassifier.is_explicit_subheading(non_empty[idx]):
                if s not in {"YES", "NO", "Yes", "No", "Why?", "Problem", "Expected Answer"}:
                    is_diag[idx] = True

    # === Pass 2: Extract flowcharts (item ↓ item ↓ item chains) ===
    first_pass = []
    i = 0
    while i < n:
        if (i + 2 < n
                and non_empty[i + 1] == '↓'
                and non_empty[i] != '↓'
                and non_empty[i + 2] != '↓'):
            items = [non_empty[i]]
            curr = i + 1
            while curr + 1 < n and non_empty[curr] == '↓' and non_empty[curr + 1] != '↓':
                items.append(non_empty[curr + 1])
                curr += 2
            first_pass.append(('FLOWCHART', items))
            i = curr
            continue
        first_pass.append(('DIAGRAM_LINE' if is_diag[i] else 'LINE', non_empty[i]))
        i += 1

    # === Pass 3: Group consecutive same-type blocks ===
    blocks = []
    i = 0
    nb = len(first_pass)
    while i < nb:
        btype, bcontent = first_pass[i]

        if btype == 'FLOWCHART':
            blocks.append(('FLOWCHART', bcontent))
            i += 1
            continue

        if btype == 'DIAGRAM_LINE':
            lines = []
            while i < nb and first_pass[i][0] == 'DIAGRAM_LINE':
                lines.append(first_pass[i][1])
                i += 1
            blocks.append(('DIAGRAM', lines))
            continue

        line = bcontent

        if LineClassifier.is_table(line):
            rows = []
            while i < nb and first_pass[i][0] == 'LINE' and LineClassifier.is_table(first_pass[i][1]):
                rows.append(first_pass[i][1])
                i += 1
            blocks.append(('TABLE', rows))
            continue

        if LineClassifier.is_asm(line):
            asm_lines = []
            while i < nb and first_pass[i][0] == 'LINE' and LineClassifier.is_asm(first_pass[i][1]):
                asm_lines.append(first_pass[i][1])
                i += 1
            blocks.append(('ASM', asm_lines))
            continue

        if LineClassifier.is_main_heading(line):
            blocks.append(('HEADING_MAIN', line))
            i += 1
            continue

        # Accumulate remaining lines as a TEXT_RUN
        text_lines = []
        while i < nb:
            ct, cc = first_pass[i]
            if ct in ('FLOWCHART', 'DIAGRAM_LINE'):
                break
            if LineClassifier.is_table(cc) or LineClassifier.is_asm(cc) or LineClassifier.is_main_heading(cc):
                break
            text_lines.append(cc)
            i += 1
        if text_lines:
            blocks.append(('TEXT_RUN', text_lines))

    # === Pass 4: Merge adjacent flowchart + diagram blocks ===
    return _merge_adjacent_blocks(blocks)


# ---------------------------------------------------------------------------
# Formatter helpers
# ---------------------------------------------------------------------------

def _format_table(rows) -> str:
    data = [[c.strip() for c in r.split('\t')] for r in rows]
    max_cols = max(len(r) for r in data)
    for r in data:
        while len(r) < max_cols:
            r.append("")
    header = data[0]
    body = data[1:]
    sep = [" :--- " for _ in range(max_cols)]
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("|" + "|".join(sep) + "|")
    for r in body:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines) + "\n"


def _format_flowchart(items) -> str:
    n = len(items)
    if n <= 4 and all(len(item) < 20 for item in items):
        return " ➔ ".join(f"**`{item.strip()}`**" for item in items) + "\n"
    lines = ["```mermaid", "flowchart TD"]
    for idx, item in enumerate(items):
        clean = item.strip().replace('"', '\\"')
        lines.append(f'    step{idx + 1}["{clean}"]')
    lines.append("    " + " --> ".join(f"step{i + 1}" for i in range(n)))
    lines.append("```\n")
    return "\n".join(lines)


def _clean_escapes(text: str) -> str:
    return text.replace(r'\_', '_').replace(r'\*', '*').replace(r'\`', '`')


LIST_INTRO_KEYWORDS = {
    "topics covered", "prerequisites", "advantages", "problems",
    "disadvantages", "interview importance", "asked almost everywhere",
    "key takeaways", "expected answer", "golden rules", "key points",
    "what you should know", "summary",
}


def _format_text_run(lines, prev_type=None, prev_content=None) -> str:
    in_list = False
    if prev_type == 'HEADING_MAIN' and isinstance(prev_content, str):
        if any(kw in prev_content.lower() for kw in LIST_INTRO_KEYWORDS):
            in_list = True

    elements = []
    paragraph = []
    list_items = []

    def flush_para():
        if paragraph:
            elements.append(("PARA", " ".join(paragraph)))
            paragraph.clear()

    def flush_list():
        if list_items:
            elements.append(("LIST", list(list_items)))
            list_items.clear()

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue

        is_explicit = line.startswith(('-', '*', '+')) or re.match(r'^\d+\.\s', line)
        is_heading = LineClassifier.is_sub_heading_candidate(raw_line)

        # Determine if this is an implicit list item
        is_implicit = False
        if not is_explicit and not is_heading:
            if in_list and len(line) < 80:
                is_implicit = True
            elif idx > 0 and lines[idx - 1].strip().endswith(':') and len(line) < 80:
                is_implicit = True
                in_list = True

        if is_explicit or is_implicit:
            flush_para()
            clean = re.sub(r'^[\-\*\+]\s+', '', line)
            clean = re.sub(r'^\d+\.\s+', '', clean)
            list_items.append(clean)
        elif is_heading:
            flush_para()
            flush_list()
            elements.append(("SUB", line))
            if any(kw in line.lower() for kw in LIST_INTRO_KEYWORDS):
                in_list = True
            else:
                in_list = False
        else:
            flush_list()
            if line.endswith(':'):
                flush_para()
                elements.append(("PARA", line))
                in_list = True
            else:
                paragraph.append(line)

    flush_para()
    flush_list()

    parts = []
    for etype, econtent in elements:
        if etype == "SUB":
            if econtent == "Expected Answer":
                parts.append("**Expected Answer:**")
            else:
                parts.append(f"### {econtent}")
        elif etype == "PARA":
            parts.append(econtent)
        elif etype == "LIST":
            parts.append("\n".join(f"- {item}" for item in econtent))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Main formatting engine
# ---------------------------------------------------------------------------

def format_document(input_path: str, output_path: str):
    blocks = parse_document(input_path)
    output = []
    i = 0
    n = len(blocks)

    while i < n:
        btype, bcontent = blocks[i]

        # ---- Main headings ----
        if btype == 'HEADING_MAIN':
            s = bcontent.strip()
            if re.match(r'^(MODULE|Module)\s+\d', s) or 'HANDBOOK' in s:
                output.append(f"# {s}\n")
            elif s == "COVER PAGE":
                output.append(f"## {s}\n")
            elif re.match(r'^Module\s+[\d\.]+\s*[—–-]', s):
                output.append(f"# {s}\n")
            else:
                output.append(f"## {s}\n")
            i += 1
            continue

        # ---- Tables ----
        if btype == 'TABLE':
            output.append(_format_table(bcontent) + "\n")
            i += 1
            continue

        # ---- Diagrams ----
        if btype == 'DIAGRAM':
            cleaned = [_clean_escapes(l) for l in bcontent]
            output.append("```text\n" + "\n".join(cleaned) + "\n```\n")
            i += 1
            continue

        # ---- Assembly blocks ----
        if btype == 'ASM':
            cleaned = [_clean_escapes(l) for l in bcontent]
            output.append("```assembly\n" + "\n".join(cleaned) + "\n```\n")
            i += 1
            continue

        # ---- Flowcharts ----
        if btype == 'FLOWCHART':
            output.append(_format_flowchart(bcontent) + "\n")
            i += 1
            continue

        # ---- Text runs ----
        if btype == 'TEXT_RUN':
            lines = bcontent
            first = lines[0].strip() if lines else ''

            # Detect Q1/Q2/... pattern inside a TEXT_RUN
            if re.match(r'^Q\d+$', first) and len(lines) > 1:
                q_label = first
                q_text = lines[1].strip()
                output.append(f"### {q_label}: {q_text}\n")
                if len(lines) > 2:
                    rest = _format_text_run(lines[2:], prev_type='HEADING_MAIN', prev_content=q_label)
                    if rest:
                        output.append(rest + "\n")
                i += 1
                continue

            # Detect Solution N / Exercise N at start of TEXT_RUN
            if re.match(r'^(Solution|Exercise)\s+\d+$', first, re.IGNORECASE):
                output.append(f"### {first}\n")
                if len(lines) > 1:
                    rest = _format_text_run(lines[1:], prev_type='HEADING_MAIN', prev_content=first)
                    if rest:
                        output.append(rest + "\n")
                i += 1
                continue

            prev_type = blocks[i - 1][0] if i > 0 else None
            prev_content = blocks[i - 1][1] if i > 0 else None
            formatted = _format_text_run(lines, prev_type=prev_type, prev_content=prev_content)
            if formatted:
                output.append(formatted + "\n")
            i += 1
            continue

        i += 1

    # Collapse triple+ newlines
    final = "\n".join(output)
    final = re.sub(r'\n{3,}', '\n\n', final)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def _get_words(text: str) -> set:
    cleaned = re.sub(r'[\#\*\_`\-\|\+]', ' ', text)
    return set(re.findall(r'\b[a-zA-Z0-9]+\b', cleaned.lower()))


def verify(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        orig = f.read()
    with open(output_path, "r", encoding="utf-8") as f:
        form = f.read()

    orig_words = _get_words(orig)
    form_words = _get_words(form)
    missing = orig_words - form_words

    if missing:
        print(f"[!] WARNING: {len(missing)} word(s) from original not found in output: {missing}")
    else:
        orig_lines = len([l for l in orig.splitlines() if l.strip()])
        form_lines = len([l for l in form.splitlines() if l.strip()])
        print(f"[OK] Verification passed -- all content words preserved.")
        print(f"     Original non-empty lines : {orig_lines}")
        print(f"     Formatted non-empty lines: {form_lines}")
        print(f"     Compression ratio         : {form_lines / orig_lines:.1%}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
        overwrite = False
    else:
        output_file = input_file
        overwrite = True

    if not os.path.isfile(input_file):
        print(f"❌ File not found: {input_file}")
        sys.exit(1)

    # Backup when overwriting
    if overwrite:
        backup = input_file + ".bak"
        shutil.copy(input_file, backup)
        print(f"[*] Backup saved: {backup}")
        tmp_output = input_file + ".tmp"
        format_document(input_file, tmp_output)
        verify(input_file, tmp_output)
        shutil.move(tmp_output, output_file)
    else:
        format_document(input_file, output_file)
        verify(input_file, output_file)

    print(f"[OK] Formatted file saved: {output_file}")
