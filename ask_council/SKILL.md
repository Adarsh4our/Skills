---
name: ask-council
description: Convenes a multi-agent council of specialized AI experts (Chief Architect, Devil's Advocate / Red Teamer, Pragmatic Staff Engineer, and Council Chairman) to deliberate through a structured multi-round debate on complex decisions, architecture choices, trade-offs, or code reviews. Use whenever the user asks to "ask council", "/ask-council", requests multi-model/multi-perspective review, or needs unbiased consensus on critical engineering decisions.
---

# Ask Council Framework — Multi-Round Debate Edition

The **Ask Council** skill convenes an expert panel that actually **debates each other's arguments** across three structured rounds before issuing a verdict. This eliminates sycophancy, forces genuine conflict resolution, and produces far sharper decisions than a single model could.

---

## The Council Seats

| Seat | Persona | Core Directive |
| :--- | :--- | :--- |
| 🏛️ **Chief Systems Architect** | Long-term structure | Modularity, scalability, domain boundaries, evolutionary design. |
| 🔍 **Devil's Advocate / Red Teamer** | Anti-sycophancy & risk | **Forbidden from agreeing.** Uncovers 3 AM failure modes, edge cases, unexamined assumptions. |
| ⚡ **Pragmatic Staff Engineer** | Simplicity & delivery | YAGNI, boring technology, TCO, minimum viable implementation. |
| ⚖️ **Council Chairman** | Binding verdict | Reads the full debate, identifies who made the stronger argument, issues a final decision. |

---

## The Three-Round Debate Protocol

```
ROUND 1 — Opening Positions (Parallel)
  Architect, Skeptic, and Pragmatist each independently state their position.
  They cannot see each other yet.
        ↓
ROUND 2 — Cross-Examination & Rebuttals (Parallel)
  Each councillor receives the other two's Round 1 positions.
  They must directly respond: agree, challenge, or modify specific points.
  Generic arguments are not allowed — they must engage with what was actually said.
        ↓
ROUND 3 — Chairman's Verdict
  The Chairman reads the full debate (Round 1 + Round 2).
  Identifies who won which argument, where consensus formed under pressure,
  and issues a binding, unambiguous final decision with a phased roadmap.
```

---

## Execution Workflow

Follow these steps precisely when running an Ask Council session.

---

### Step 1: Frame the Dilemma Neutrally

Before dispatching, strip any leading bias from the user's question.
- Do NOT phrase the prompt to favour one option.
- Include: the core question, relevant constraints (stack, team size, traffic, budget), and the options being considered.

---

### Step 2: Round 1 — Opening Positions (Parallel Dispatch)

Invoke all three councillors **simultaneously** using `invoke_subagent`.

For each subagent, include:
- Their persona system prompt from [personas.md](./references/personas.md) — specifically the **Round 1 Opening** prompt.
- The full neutrally-framed dilemma.
- The instruction: *"Do NOT see or reference any other councillor's position yet. Give your independent opening stance."*

```json
[
  { "Role": "Chief Systems Architect", "TypeName": "self", "Model": "pro", "Prompt": "<Architect R1 Prompt + Dilemma>" },
  { "Role": "Devil's Advocate / Red Teamer", "TypeName": "self", "Model": "pro", "Prompt": "<Skeptic R1 Prompt + Dilemma>" },
  { "Role": "Pragmatic Staff Engineer", "TypeName": "self", "Model": "pro", "Prompt": "<Pragmatist R1 Prompt + Dilemma>" }
]
```

Wait for all three to complete before proceeding.

---

### Step 3: Round 2 — Cross-Examination & Rebuttals (Parallel Dispatch)

Now feed each councillor the **other two's Round 1 outputs** and ask for their rebuttal.

Use the **Round 2 Cross-Examination** prompts from [personas.md](./references/personas.md).

Each subagent receives:
- Their persona's Round 2 system prompt.
- Their own Round 1 position.
- The other two councillors' Round 1 positions verbatim.
- The instruction: *"You MUST directly engage with the specific arguments made by the other seats. Do not write generic points. Quote or reference their actual claims and agree, challenge, or refine them."*

Dispatch all three rebuttals simultaneously and wait for completion.

---

### Step 4: Round 3 — Chairman's Verdict

The primary agent now assumes the role of **Council Chairman**.

Read the complete debate thread:
1. All three Round 1 opening positions.
2. All three Round 2 rebuttals.

Then produce the final verdict following the structure in [council_report_template.md](./templates/council_report_template.md):

- **Who won which argument?** (Which councillor's point held up under cross-examination vs. got dismantled?)
- **Where did genuine consensus form under pressure?** (Points that survived rebuttal from all three.)
- **What is the irreconcilable core tension?** (The trade-off the Chairman must break by judgement.)
- **Binding final decision** — unambiguous. No "it depends." Give a clear recommendation.
- **Phased roadmap** — concrete next steps.

Create this as an artifact named `council_deliberation.md`.

---

## Notes

- **Total rounds:** 3 (R1 parallel → R2 parallel → Chairman synthesis)
- **Time:** Longer than a single-pass council but produces dramatically sharper, more trustworthy decisions.
- **For the headless/terminal version**, see [execution_modes.md](./references/execution_modes.md) and run `scripts/council_runner.py`.
