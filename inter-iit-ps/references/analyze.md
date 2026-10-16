# Analyze a Problem Statement (PS)

## Ingestion and Provenance

Locate the supplied problem statement. The input may be a PDF, a Markdown document, plain text, an HTML/web export, a directory of problem files, or text pasted directly into the session.

Use the bundled ingestion helper to produce standardized `ps.txt` and `extraction.json`:

~~~powershell
python "<skill-folder>/scripts/ingest_ps.py" "<input-path-or-folder>" "<output-ps-folder>"
~~~

- **PDF Inputs:** Extracted via PyMuPDF with numbered page markers (`===== PDF PAGE X OF Y =====`) and visual review flags for sparse pages, scoring tables, or architectural diagrams.
- **Markdown / Text / Multi-file Inputs:** Extracted preserving document structure, headings, lines, and source checksums.
- **Pasted / In-Session Text:** If no local file path exists, write the provided text directly into `ps.txt` inside the PS folder and generate a minimal `extraction.json`.

If PyMuPDF is unavailable for PDF files, use another available extractor (e.g., `pdftotext -layout` or OCR tools) and record the extraction method in `context.md`. Retain page/document breaks and never replace or overwrite the source material.

- Check extracted text against page/section counts. Visually inspect sparse pages, equations, scoring tables, and architectural diagrams.
- For image-based or scanned pages, transcribe or OCR faithfully, noting any uncertain symbols.
- Keep extraction faithful: headers, units, constraints, formulas, and rules belong in `ps.txt`. Interpretations belong in `analysis.md`.

---

## analysis.md

Produce a clear, structured breakdown explaining what the organizers/stakeholders want and how solutions will be evaluated. Populate only sections supported by the PS:

1. **Plain-Language Problem & Objective:**
   What needs to be built, investigated, or demonstrated? Who are the stakeholders or target users? Why does this problem matter?

2. **Input → Processing → Output Pipeline:**
   - **Inputs:** Supplied datasets, APIs, sensory inputs, simulator environments, hardware specifications, starter code.
   - **Processing:** Required transformations, reasoning, algorithmic pipelines, control loops, or model inferences.
   - **Outputs:** Expected predictions, UI dashboards, control outputs, artifacts, or trained weights.

3. **Requirements & Constraints:**
   - **Mandatory vs. Optional / Bonus:** Distinguish core criteria from stretch goals.
   - **Hard Constraints:** Compute limits (e.g. CPU-only, VRAM caps, edge devices), latency/memory thresholds, offline requirements, allowed vs. prohibited libraries/APIs, dataset usage rules, and deadlines.

4. **Deliverables & Evaluation Criteria:**
   - What the team must submit (code repository, technical report, docker container, demo video, presentation).
   - Evaluation metrics: Quantitative formulas (e.g. accuracy, F1, latency, throughput, R², BLEU, custom scoring formulas) vs. Qualitative scoring (innovation, system design, presentation).
   - Important edge cases and disqualification rules.

5. **Skills & Capabilities Needed:**
   Map the technical competencies required to solve the PS. Explicitly distinguish **mandated technologies** (e.g., "Must use PyTorch and ROS2") from **inferred implementation choices** (e.g., "FastAPI recommended for serving").

6. **Ambiguities, Hidden Assumptions & Questions:**
   Document missing parameters, contradictory guidelines, unstated test environments, or ambiguous scoring criteria that require user or organizer clarification.

---

## Citation and Handoff

- Cite exact locations: "PDF p. 4" for PDFs, section names / lines for text and markdown documents.
- Record exact formulas and thresholds where provided.
- Mark inferred needs as *inferred* and absent details as *unspecified*. Avoid presenting an unsupported final design in this stage.
- Save `analysis.md` and initialize or update `context.md`.
- Provide the user with a concise summary of the core objective, constraints, deliverables, and top open questions, linking directly to `ps.txt` and `analysis.md`.
