---
name: problem-statement
description: In-depth analysis, literature/technical research, and tailored proposal or application drafting for ANY Problem Statement (PS) — including Inter-IIT Tech Meet, Smart India Hackathon (SIH), Kaggle/competitions, case challenges, research grants, and enterprise RFPs. Supports multi-format ingestion (PDF, text, markdown, web), requirements extraction, baseline-to-advanced solution architectures, and non-hallucinatory candidate application drafting. Use when the user says analyze this PS, explain problem statement, research this PS, draft proposal for PS, or answer PS application questions.
---

# Problem Statement (PS) Assistant

A universal, evidence-grounded framework to solve any technical problem statement across three independent or combined stages: **analyze**, **research**, and **apply**.

Execute only the stage requested by the user. If the user asks to "analyze first", stop after extraction, structured analysis, and explanation.

---

## Shared Context & Directory Architecture

Organize each problem statement in a dedicated folder:
1. **User-specified path:** Always honor an explicit destination path if provided.
2. **Active Workspace:** If working inside a project/workspace repository, default to `./ps-solutions/<ps-slug>/` or `./problem-statements/<ps-slug>/`.
3. **Global Library:** Otherwise, default to `C:/Users/Adarsh Singh/Documents/Problem-Statements/<ps-slug>/` (or `C:/Users/Adarsh Singh/Documents/Inter-IIT/<ps-slug>/` for Inter-IIT PSs).

Derive `<ps-slug>` from the PS title and organizer/sponsor. Add a short input hash if titles collide. Reuse the same folder for the same PS; do not mix distinct problem statements.

| Artifact | Purpose |
|---|---|
| `ps.txt` | Standardized extracted PS text (preserving PDF pages or markdown/doc boundaries) |
| `extraction.json` | Provenance metadata, source SHA-256 hash, format diagnostics, and visual review alerts |
| `analysis.md` | Structured 6-part requirements breakdown and plain-language explanation |
| `research.md` | Primary literature notes, comparative approach matrix, and next-agent architecture handoff |
| `application.md` | Copy-ready application answers or technical proposal, verified counts, and evidence notes |
| `context.md` | Persistent index and state handoff allowing any agent to resume without chat context |

After every stage, update `context.md` with: PS title, source path/hash, completed stages, artifact paths, extraction caveats, recorded user decisions, pending questions, loaded experience profile, and recommended next steps.

---

## Experience Profile Resolution

When drafting applications or proposals, resolve the candidate experience source in priority order:
1. User-supplied path in prompt or `context.md`.
2. Workspace profile: `./experience.md`, `./profile.md`, or `./resume.md`.
3. Global default profile: `C:/Users/Adarsh Singh/Documents/inter-iit-experience.md` or the `user-profile` skill.
4. Fallback: If no profile exists, draft the technical solution fully and scaffold personal experience with clear `[Insert your experience with X]` placeholders.

---

## Stage Routing

### 1. Analyze / Explain this PS
*Reference: [references/analyze.md](references/analyze.md)*

- Ingest the input file (PDF, Markdown, plain text, web page, or pasted text) using `scripts/ingest_ps.py` into `ps.txt` and `extraction.json`.
- Check page/section coverage; inspect sparse pages, scoring formulas, and architecture diagrams visually.
- Produce `analysis.md` covering: Problem & Context, I/O Pipeline, Requirements & Constraints, Deliverables & Evaluation Criteria, Skills Matrix, and Ambiguities.
- Initialize `context.md` and present a clear, plain-language explanation to the user.

### 2. Research / Technical Deep Dive
*Reference: [references/research.md](references/research.md)*

- Reuse existing `ps.txt`, `analysis.md`, and `context.md`. If starting directly here, perform Stage 1 first.
- Construct a targeted search map across primary literature (arXiv, IEEE, ACM, NeurIPS), benchmark datasets, and analogous competition winning solutions.
- Compile `research.md` featuring verified paper notes (`[R1]`, `[R2]`), an Approach Comparison Matrix (Baseline vs. SOTA vs. Alternatives across compute, data, feasibility, licensing), and a concrete 3-phase execution roadmap.
- Update `context.md` with findings and next-step recommendations.

### 3. Apply / Draft Proposal or Answers
*Reference: [references/application.md](references/application.md)*

- **Custom Prompts (Mode A):** If the user provides specific form questions or an application template (e.g. hackathon submission, SIH idea slip, YC form), draft exact answers respecting word/character limits.
- **Competitive Recruitment (Mode B - Default):** Draft the two standard competitive recruitment questions:
  1. *Experience & Fit:* Candidate's verified project experience mapped directly to the PS needs.
  2. *Proposed Solution:* Phased technical approach and team execution roadmap.
- **Full Proposal (Mode C):** When requested, compile an executive technical proposal covering architecture, data flow, feasibility, and milestone timeline.
- Enforce strict truthfulness: no fabricated metrics, respect team attribution boundaries, and preserve simulation/prototype qualifiers.
- Write in clean, simple English: avoid overly complex, convoluted jargon or unnatural "high-fi" vocabulary so application answers read easily and naturally.
- Save `application.md` with copy-ready answers and exact counts, and update `context.md`.

---

## Examples

- *"Analyze this problem statement PDF first."* → Ingestion, 6-part analysis, plain-language explanation, saved `context.md`.
- *"Research viable approaches for this PS."* → Literature search, baseline vs. SOTA comparison matrix, saved `research.md`.
- *"Answer my recruitment questions for this PS: 150 words each."* → Tailored copy-ready answers mapped to verified experience profile.
- *"Draft a hackathon proposal for this problem statement using these 3 custom questions."* → Answers to the 3 custom prompts adhering to constraints.
- *"Solve this PS end-to-end: analyze, research the literature, and draft the solution roadmap."* → Sequential execution across all stages with full provenance.
