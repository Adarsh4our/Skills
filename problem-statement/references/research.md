# Research a PS into a Detailed Technical Packet

## Establish Research Questions

Read the current `ps.txt`, `analysis.md`, `context.md`, and any user clarifications. Resolve unreadable or missing requirements before relying on them.

Construct a systematic search map from the PS requirements:
- Core domain concepts and theoretical formulations.
- Required capabilities, algorithms, model architectures, and data/simulation pipelines.
- Standard evaluation benchmarks, datasets, and winning competition baselines (e.g., Kaggle, CVPR/NeurIPS challenges, previous Inter-IIT / SIH top solutions).
- Known failure modes, computational bottlenecks, and edge-case fragility.
- Hardware, memory, compute budget, and license constraints.

Investigate each material topic thoroughly. Continue searching until viable candidate approaches are understood, evidence is gathered for main trade-offs, and searches yield diminishing returns. Explicitly document any remaining technical uncertainties.

---

## Literature & Source Review

Browse the internet actively during this stage. Prioritize:
1. **Primary Research Papers:** Original papers (arXiv, IEEE, ACM, NeurIPS, CVPR, ICRA, etc.). Check publication venue, year, authors, and DOI / arXiv links.
2. **Official Documentation & Starter Repositories:** Framework docs, official dataset benchmarks, PyTorch/TensorFlow implementations, and verified GitHub repositories.
3. **Competition Write-ups:** Post-competition technical notes and solution write-ups for analogous challenges.

**Verification Standards:**
- Open sources and inspect actual methods, tables, ablation studies, and limitations.
- Distinguish between full-text reading, partial skimming, and abstract-only access. Do not claim a paper was fully analyzed based on a snippet or abstract alone.
- Note experimental conditions (e.g., dataset, compute hardware, metric, split). Do not assume reported paper metrics will transfer directly to the PS without validation.
- Verify software repository activity, licensing (e.g., MIT, Apache 2.0 vs. non-commercial CC-BY-NC), dependency requirements, and model weight availability.
- When sources disagree or report conflicting performance, explain the discrepancy and what conditions differentiate them.

---

## research.md Structure

Produce a self-contained technical packet that any team member or agent can execute without conversation history. Structure the report around the PS rather than as an unorganized bibliography:

1. **PS Identity & Research Scope:**
   Link source analysis, state investigation date, and list requirements/hypotheses investigated along with explicit boundaries.

2. **Technical Foundations & Architecture:**
   Explain the foundational concepts, data flows, and algorithms needed to reason about the problem. Map each PS requirement to relevant technical literature.

3. **Source & Paper Dossiers:**
   Assign stable identifiers (`[R1]`, `[R2]`, ...). For key sources, record:
   - Full citation (Title, Authors, Year, Venue, Link).
   - Review depth (Full text, methods/results only, abstract).
   - Core methodology and key takeaways.
   - Identified limitations and explicit applicability to this PS.

4. **Approach Comparison Matrix:**
   Compare a solid baseline against state-of-the-art and alternative candidate approaches across:
   - Feasibility and implementation complexity.
   - Compute, memory, and hardware budget fit.
   - Data / training requirements.
   - Expected failure modes and mitigation strategies.
   - License and intellectual property compatibility.

5. **Recommended Solution Architecture & Execution Path:**
   - **Phase 1: Working Baseline** (Simple, robust end-to-end prototype).
   - **Phase 2: Core Enhancements** (Model scaling, domain adaptations, feature engineering, pipeline optimization).
   - **Phase 3: Final Polish & Verification** (Ablations, ensemble strategies, latency tuning, packaging).
   - Proposed validation experiments, evaluation metrics, and ablation tests.

6. **Risks, Bottlenecks & Unresolved Questions:**
   Clearly separate verified empirical facts from speculative hypotheses. Highlight critical dependencies that could change the recommended path.

7. **Next-Agent / Team Handoff:**
   Enumerate files to inspect, the primary recommended technical path, recorded decisions, open questions, and the immediate next actionable task.

---

## Finish & Handoff

- Verify that every material requirement from `analysis.md` is addressed or marked as an explicit research gap.
- Save `research.md` and update `context.md`.
- Keep chat output concise: summarize the top recommended approach, highlight key tradeoffs or risks, and link directly to `research.md`.
