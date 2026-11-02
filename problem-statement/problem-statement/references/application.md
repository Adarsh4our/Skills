# Draft Application Answers or Technical Proposals

## Experience Evidence Resolution

Read the selected PS's `context.md`, `analysis.md`, original PS text, and any available `research.md`.

Locate the candidate experience profile in order of priority:
1. **User-specified path:** Path provided in the user prompt or stored in `context.md`.
2. **Workspace profile:** `./experience.md`, `./profile.md`, or `./resume.md` in the current project root.
3. **Global default profile:** `C:/Users/Adarsh Singh/Documents/inter-iit-experience.md` or the `user-profile` skill.
4. **Fallback (No Profile Available):** If no profile exists, draft the technical execution answer fully, and for personal experience, provide a tailored outline highlighting the exact technical competencies needed with structured `[Insert your project / experience with X]` placeholders.

---

## Operating Modes

### Mode A: Custom Application Form / Questions (User-Supplied)
When the user or competition provides specific form prompts (e.g., hackathon portal fields, Google Forms, Smart India Hackathon idea templates, conference/grant applications):
- Parse each question and its stated word or character constraint.
- Address the exact question intent directly, without rambling.
- Match relevant projects and technical evidence from the experience profile to each question.

### Mode B: Standard Competitive Application (Default)
When no custom questions are supplied, draft the two standard competitive recruitment/selection questions:

1. **Applicant Fit & Technical Experience:**
   *What is your experience with the technologies/skills required for this problem statement, and why are you a strong applicant?*
   - Written in natural, direct first person.
   - Connect 1–3 concrete, verified projects from the experience profile directly to the PS's core requirements.
   - Detail the applicant's specific contribution, technical decisions made, and verified outcomes.

2. **Proposed Technical Approach & Execution Roadmap:**
   *How do you propose to approach and solve the problem statement end-to-end?*
   - Outline a credible, phased engineering plan:
     - Requirement confirmation and data/simulation pipeline setup.
     - Robust baseline implementation and core processing flow.
     - Advanced modeling, performance optimization, and ablation testing.
     - Deliverable packaging, testing, and metric validation against the PS rubrics.
   - Draw on `research.md` to justify key architectural choices and trade-offs.

### Mode C: Technical Project Proposal / Executive Pitch
When the user asks for a project proposal or pitch:
- Executive Summary & Problem Framing.
- System Architecture & Core Technology Stack.
- Data Pipeline & Modeling / Algorithmic Flow.
- Feasibility, Risk Mitigation & Milestone Schedule.

---

## Evidentiary Standards & Voice

- **Attribution & Team Boundaries:** Dynamically inspect the loaded profile for team vs. individual ownership. Distinguish personal contributions from overall team achievements.
- **Zero Fabrication:** Never invent performance metrics (e.g. speedups, accuracy, R²), production deployments, active users, awards, leadership titles, or unverified hardware tests.
- **Preserve Qualifiers:** Retain simulation, prototype, and educational qualifiers where applicable.
- **Tone & Language:** Use clean, simple, and natural English. Avoid overly complex sentence structures, convoluted jargon, or unnatural "high-fi" vocabulary. Keep sentences direct, grounded, and easily readable in one pass while preserving technical precision.
- **Distinction of Voice:** Maintain a crisp distinction between past completed work ("I implemented...") and proposed future architecture ("We propose...").

---

## Length Limits and Output Contract

- Adhere strictly to the requested word or character cap (per answer or total as specified).
- If no word limit is provided, default to **150 words per answer** for recruitment questions.
- Count words/characters accurately using a local tool or script; do not guess counts.

Save `application.md` with:
1. **Copy-Ready Answers:** Each question and its final text, formatted for immediate submission.
2. **Word / Character Counts:** Stated explicitly alongside each answer.
3. **Evidence & Source Audit:** A concise separate note identifying the specific profile projects and research papers backing each technical claim.
4. **Pending Clarifications:** Highlight any missing personal details or assumptions outside the copy-ready answers.

Update `context.md` and present the copy-ready answers in the chat response.
