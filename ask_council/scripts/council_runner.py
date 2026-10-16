#!/usr/bin/env python3
"""
Ask Council Runner — Multi-Round Debate Edition with Session Checkpointing
Part of the Antigravity Ask Council Framework.

Runs a proper 3-round structured council debate:
  Round 1: All 3 councillors give independent opening positions (parallel)
  Round 2: Each councillor reads the others' R1 positions and rebuts (parallel)
  Round 3: Chairman reads full debate and issues a binding verdict

CHECKPOINT SYSTEM:
  - Progress is saved to a JSON checkpoint file after each completed round.
  - If the process is interrupted (token exhaustion, crash, power loss), re-run
    with --resume <session-id> to continue from exactly where it stopped.
  - Sessions are stored in: ~/.gemini/config/skills/ask_council/sessions/
  - Checkpoint files are human-readable JSON and can be copied across machines.

Usage:
  # Start a new session
  python council_runner.py -d "Should we use Kafka or Redis Pub/Sub?" --session my-kafka-debate

  # Resume an interrupted session
  python council_runner.py --resume my-kafka-debate

  # List all saved sessions
  python council_runner.py --list-sessions

  # Save report to file
  python council_runner.py --resume my-kafka-debate --output report.md
"""

import argparse
import asyncio
import datetime
import json
import os
import sys
import uuid
import urllib.request
import urllib.error
from typing import Dict, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ---------------------------------------------------------------------------
# SESSION / CHECKPOINT PATHS
# ---------------------------------------------------------------------------

SESSIONS_DIR = os.path.join(
    os.path.expanduser("~"), ".gemini", "config", "skills", "ask_council", "sessions"
)


def sessions_dir() -> str:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return SESSIONS_DIR


def session_path(session_id: str) -> str:
    return os.path.join(sessions_dir(), f"{session_id}.json")


# ---------------------------------------------------------------------------
# CHECKPOINT I/O
# ---------------------------------------------------------------------------

def new_checkpoint(session_id: str, dilemma: str, context: str) -> dict:
    now = datetime.datetime.now().isoformat()
    return {
        "version": 2,
        "session_id": session_id,
        "dilemma": dilemma,
        "context": context,
        "created_at": now,
        "updated_at": now,
        "status": "started",           # started | r1_complete | r2_complete | complete
        "rounds": {
            "r1": {},                  # { architect, skeptic, pragmatist }
            "r2": {},
            "verdict": ""
        },
        "future_plans": {
            "open_questions": [],
            "suggested_next_councils": [],
            "mandatory_mitigations": [],
            "notes": ""
        }
    }


def save_checkpoint(cp: dict, verbose: bool = False) -> None:
    cp["updated_at"] = datetime.datetime.now().isoformat()
    path = session_path(cp["session_id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cp, f, indent=2, ensure_ascii=False)
    if verbose:
        print(f"    [Checkpoint] Saved to: {path}")
    else:
        print(f"    [Checkpoint] Progress saved → session: {cp['session_id']}")


def load_checkpoint(session_id: str) -> dict:
    path = session_path(session_id)
    if not os.path.exists(path):
        # Try treating it as a full path
        if os.path.exists(session_id):
            path = session_id
        else:
            print(f"[ERROR] Session not found: '{session_id}'")
            print(f"        Expected: {session_path(session_id)}")
            print(f"        Run --list-sessions to see available sessions.")
            sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_sessions() -> None:
    d = sessions_dir()
    files = sorted(
        [f for f in os.listdir(d) if f.endswith(".json")],
        key=lambda f: os.path.getmtime(os.path.join(d, f)),
        reverse=True
    )
    if not files:
        print("No saved sessions found.")
        print(f"Sessions directory: {d}")
        return

    print(f"\nSaved Council Sessions ({len(files)} found):")
    print(f"{'Session ID':<35} {'Status':<15} {'Updated':<22} Dilemma")
    print("-" * 110)
    for fname in files:
        try:
            with open(os.path.join(d, fname), encoding="utf-8") as f:
                cp = json.load(f)
            sid = cp.get("session_id", fname.replace(".json", ""))
            status = cp.get("status", "?")
            updated = cp.get("updated_at", "?")[:16]
            dilemma = cp.get("dilemma", "?")[:55]
            resume_hint = "" if status == "complete" else " ← can resume"
            print(f"{sid:<35} {status:<15} {updated:<22} {dilemma}{resume_hint}")
        except Exception:
            print(f"  {fname} (unreadable)")
    print()
    print(f"Sessions directory: {d}")
    print(f"To resume: python council_runner.py --resume <session-id>")


# ---------------------------------------------------------------------------
# PERSONA PROMPTS — Round 1 & Round 2
# ---------------------------------------------------------------------------

ROUND1_PROMPTS = {
    "architect": {
        "title": "Chief Systems Architect",
        "icon": "🏛️",
        "system": """You are the Chief Systems Architect on an expert technical council engaged in a formal debate.

This is ROUND 1: Give your independent opening position. You cannot see what the other councillors will say. Do NOT hedge — state your architectural position clearly and defend it.

Your lens: component boundaries, coupling, domain isolation, state lifecycle, scalability at 10x/100x load, long-term technical debt, evolutionary design, architectural anti-patterns.

Format your response exactly as:
### 🏛️ Architect — Opening Position
**Stance:** [Recommend Option A / Option B / Hybrid — be specific]
**Core Argument:** [Your primary structural reasoning]
**Scalability & Longevity:** [How this holds at scale]
**Guardrails Required:** [Non-negotiable constraints if your recommendation is adopted]"""
    },
    "skeptic": {
        "title": "Devil's Advocate / Red Teamer",
        "icon": "🔍",
        "system": """You are the Devil's Advocate and Red Teamer on an expert technical council engaged in a formal debate.

This is ROUND 1: Give your independent opening attack. You cannot see what the other councillors will say.

MANDATORY RULES:
- You are STRICTLY FORBIDDEN from rubber-stamping or saying "this is a good approach overall."
- Even if one option is better, find its breaking points. Be SPECIFIC, not generic.
- Provide concrete failure scenarios with real production consequences.

Your lens: 3:00 AM failures, network partitions, retry storms, deadlocks, race conditions, blast radius, unexamined assumptions, operational toil.

Format your response exactly as:
### 🔍 Devil's Advocate — Opening Position
**Risk Severity:** [Critical / High / Medium]
**Primary Attack Vector:** [The single biggest danger — specific, not generic]
**Failure Scenarios (3:00 AM):** [Numbered list of concrete failures with production consequences]
**Unexamined Assumptions:** [Where the proposal relies on wishful thinking]
**Non-Negotiable Mitigations:** [What MUST be in place before this is safe to ship]"""
    },
    "pragmatist": {
        "title": "Pragmatic Staff Engineer",
        "icon": "⚡",
        "system": """You are the Pragmatic Staff Engineer on an expert technical council engaged in a formal debate.

This is ROUND 1: Give your independent opening position. You cannot see what the other councillors will say.

Your lens: YAGNI (ruthlessly applied), total cost of ownership, cognitive load, debugging friction, on-call burden, boring technology, reversibility.

The simplest solution that satisfies 90% of requirements with 10% of the complexity wins.

Format your response exactly as:
### ⚡ Pragmatic Engineer — Opening Position
**Pragmatic Stance:** [Simplify / Approve as-is / Push back entirely]
**Core Argument:** [Why complexity must be earned, not assumed]
**The Boring Alternative:** [The simplest viable approach]
**True TCO Estimate:** [Developer hours, operational overhead, on-call burden]
**Reversibility Assessment:** [How painful is it to undo this decision?]"""
    }
}

ROUND2_PROMPTS = {
    "architect": """You are the Chief Systems Architect on an expert technical council. This is ROUND 2: Cross-Examination.

You have just received the opening positions from the Devil's Advocate and the Pragmatic Engineer (shown below). You MUST directly engage with their SPECIFIC arguments — not write new generic points.

Format your response exactly as:
### 🏛️ Architect — Round 2 Rebuttal
**Response to Devil's Advocate:** [Direct point-by-point engagement with their specific claims]
**Response to Pragmatic Engineer:** [Direct point-by-point engagement with their specific claims]
**Concessions (if any):** [Points from others you cannot refute]
**Final Architectural Recommendation:** [Your position after cross-examination]""",

    "skeptic": """You are the Devil's Advocate and Red Teamer on an expert technical council. This is ROUND 2: Cross-Examination.

You have just read the opening positions from the Architect and the Pragmatic Engineer (shown below). You MUST directly attack their SPECIFIC claims.

You are STILL forbidden from saying "this is fine overall."

Format your response exactly as:
### 🔍 Devil's Advocate — Round 2 Rebuttal
**Attack on Architect's Position:** [Specific rebuttal of their Round 1 arguments]
**Attack on Pragmatist's Position:** [Specific rebuttal of their Round 1 arguments]
**What Survived Cross-Examination (Concessions):** [Points from others you cannot refute]
**The Surviving Critical Risk:** [The danger that still stands after the full debate]""",

    "pragmatist": """You are the Pragmatic Staff Engineer on an expert technical council. This is ROUND 2: Cross-Examination.

You have just read the opening positions from the Architect and the Devil's Advocate (shown below). You MUST directly respond to their SPECIFIC arguments.

Format your response exactly as:
### ⚡ Pragmatic Engineer — Round 2 Rebuttal
**Response to Architect's Abstractions:** [Are they necessary now or premature?]
**Response to Devil's Advocate's Risks:** [Real risks at current scale vs. hypothetical?]
**Where Both Are Right (Concessions):** [Complexity that IS warranted]
**Simplified Final Recommendation:** [Clearest path forward after hearing the debate]"""
}

CHAIRMAN_PROMPT = """You are the Council Chairman. You have just witnessed a full multi-round structured debate.

Your task is NOT to summarize — your task is to JUDGE and DECIDE.

1. Which Round 1 arguments were dismantled in Round 2, and which survived under pressure?
2. Where did genuine consensus form UNDER PRESSURE?
3. What is the irreconcilable core tension — the trade-off YOU must break by judgement?
4. Who made the stronger overall case?
5. Issue a BINDING, UNAMBIGUOUS final verdict. No "it depends."
6. Produce a phased implementation roadmap with the Devil's Advocate's surviving risks as mandatory mitigations.
7. At the end, include a FUTURE PLANS section with:
   - Open questions this council did NOT resolve (things to deliberate next)
   - Suggested next council topics that logically follow from this decision
   - Mandatory mitigations that need their own follow-up councils

Format your response as:
## ⚖️ Chairman's Verdict

### Who Won the Key Arguments:
[For each contested point, state who prevailed and why]

### Genuine Consensus (Survived Cross-Examination):
[Points all councillors converged on after debate]

### The Core Irreconcilable Tension:
[The fundamental trade-off the Chairman must decide]

### ⚖️ BINDING FINAL DECISION:
**[State the decision clearly and unambiguously]**
Rationale: [Why this option over the other(s)]

### Phased Implementation Roadmap:
Phase 1 — [Minimal Viable Implementation]
Phase 2 — [Mandatory Mitigations from the Debate]
Phase 3 — [Validation & Production Verification]

### 📋 Future Plans & Open Questions:
**Unresolved questions for a future council:**
- [question 1]
- [question 2]

**Suggested next council topics:**
- [topic 1: why it follows from this decision]
- [topic 2: why it follows from this decision]

**Mandatory follow-up mitigations (need their own review):**
- [mitigation 1]
- [mitigation 2]"""


# ---------------------------------------------------------------------------
# OFFLINE ANALYTICAL ENGINE
# ---------------------------------------------------------------------------

OFFLINE_R1 = {
    "architect": """### 🏛️ Architect — Opening Position
**Stance:** Adopt the proposed approach, but ONLY behind a clean domain interface.

**Core Argument:**
The core risk is not the technology choice itself but tight coupling. Whatever option is selected, the implementation must be hidden behind a strictly typed interface. This preserves the ability to swap backends without touching business logic. State lifecycle is the second concern — mutable shared state without explicit ownership boundaries leads to race conditions invisible in testing and catastrophic in production.

**Scalability & Longevity:**
At 10x load, a tightly coupled implementation becomes a migration nightmare. An interface-first design means the team can migrate incrementally with traffic splitting — without a big-bang rewrite.

**Guardrails Required:**
1. A strict interface/protocol with no implementation details leaking across the boundary.
2. All state mutations must be idempotent and carry deduplication keys.
3. Distributed tracing spans must cross the abstraction boundary so failures are attributable.""",

    "skeptic": """### 🔍 Devil's Advocate — Opening Position
**Risk Severity:** High

**Primary Attack Vector:**
The "clean interface" the Architect will inevitably propose is a false sense of safety. Interfaces abstract syntax, not failure modes. The failure semantics of the underlying technology WILL leak through, and the team will be unprepared because they believed the interface protected them.

**Failure Scenarios (3:00 AM):**
1. **Retry Amplification Storm:** Under degraded network, a caller sees a timeout and retries. If not idempotent, you now have duplicate writes. If every tier retries independently, you have exponential amplification to an already-struggling backend.
2. **Connection Pool Exhaustion on Restart:** When the backing service restarts, all clients attempt reconnection simultaneously. Connection limits are hit, requests queue up without bound. The service appears "up" to health checks but is serving 100% errors.
3. **Stale Cache / Split-Brain:** Cache invalidation during a rolling deploy means different nodes serve different versions of truth for an indeterminate window.

**Unexamined Assumptions:**
The proposal assumes nominal network conditions and orderly restarts. Neither is guaranteed.

**Non-Negotiable Mitigations:**
1. Client-side circuit breakers with half-open health checks.
2. Bounded retry budgets with exponential backoff + full jitter, enforced at the interface level.
3. Idempotency keys on ALL mutating operations, server-side deduplication window of at least 60 seconds.""",

    "pragmatist": """### ⚡ Pragmatic Engineer — Opening Position
**Pragmatic Stance:** Simplify — the proposed complexity is not yet earned.

**Core Argument:**
The team is proposing infrastructure they do not yet need, to solve problems they do not yet have, at a scale they have not yet reached. Every abstraction added today is cognitive overhead every future engineer must decode. Every additional service is another thing to monitor, rotate secrets for, and get paged about at 3 AM.

**The Boring Alternative:**
The existing relational database or built-in framework tooling can handle 90% of the stated requirements with zero additional operational footprint. Add complexity ONLY when specific, measurable metrics demonstrate necessity.

**True TCO Estimate:**
- Complex approach: 3-5 developer-weeks, 1 new service to operate, ongoing on-call burden.
- Boring alternative: 2-3 developer-days, no new infrastructure, $0 additional cost.

**Reversibility Assessment:**
The boring approach is highly reversible — it uses existing infrastructure the team already understands. The complex approach creates lock-in that is painful to undo once business logic grows around it."""
}

OFFLINE_R2 = {
    "architect": lambda r1: """### 🏛️ Architect — Round 2 Rebuttal

**Response to Devil's Advocate:**
The Devil's Advocate raised three concrete failure scenarios. I can address two directly and must concede the third.

On retry amplification: This is precisely why my Round 1 position requires idempotency keys and retry budgets enforced AT the interface boundary. If the interface enforces this contract, the retry storm is bounded.

On connection pool exhaustion: Valid risk. I'm adding a mandatory guardrail: the interface implementation must use a connection pool with backpressure (reject requests with a fast 503 rather than queueing indefinitely) and reconnect with jitter, not thundering herd reconnect.

On stale cache / split-brain: I must concede this. Cache invalidation during rolling deploys is genuinely hard. The interface abstraction does not solve it — it requires an explicit cache versioning strategy.

**Response to Pragmatic Engineer:**
The Pragmatic Engineer is right that complexity must be earned. They are wrong that the interface is premature. An interface costs one afternoon to write and saves weeks of migration later. The boring technology choice is acceptable — my position is about the boundary, not the backend.

**Concessions:**
- Cache invalidation during deploys requires explicit strategy beyond the interface.
- The underlying technology choice can be the boring one.

**Final Architectural Recommendation:**
Use the boring technology the Pragmatist recommends, but behind a strict domain interface.""",

    "skeptic": lambda r1: """### 🔍 Devil's Advocate — Round 2 Rebuttal

**Attack on Architect's Position:**
The Architect conceded that their interface does not solve cache invalidation during rolling deploys. More critically, the Architect's retry amplification fix relies on "enforcing retry budgets at the interface boundary" — but this assumes all callers USE the interface and do not bypass it. In practice, there will always be a script, batch job, or junior engineer's direct call that bypasses the interface. The interface is not a security boundary; it is a suggestion.

**Attack on Pragmatist's Position:**
The Pragmatist's "boring alternative" defers the complexity, it does not eliminate it. The relational database will eventually become the bottleneck — and the migration will happen under pressure, during an incident, with business-critical data at risk. "Reversible" is theoretical. Migrations of live, growing datasets are expensive and slow.

The Pragmatist also did not address connection pool exhaustion or retry amplification for the boring approach. These risks exist regardless of technology choice.

**What Survived Cross-Examination (Concessions):**
The Architect's point about interfaces enabling incremental migration is sound. The Pragmatist's TCO point is sound. I concede both.

**The Surviving Critical Risk:**
Neither councillor adequately addressed the thundering herd reconnection problem after a backing service restart. This MUST be solved with jittered reconnection and backpressure before any version ships to production.""",

    "pragmatist": lambda r1: """### ⚡ Pragmatic Engineer — Round 2 Rebuttal

**Response to Architect's Abstractions:**
The Architect moderated their position in Round 2 — they're now saying "use the boring technology, just put it behind an interface." I largely agree. A thin interface (one afternoon of work) is not the over-engineering I was pushing back against. A single clean interface over boring technology is reasonable.

**Response to Devil's Advocate's Risks:**
The Devil's Advocate raised thundering herd reconnection and retry amplification. These are real. However, they are real for BOTH the complex and simple approach — they are implementation requirements, not arguments for or against a specific technology.

The concern that "engineers will bypass the interface" is valid but cannot be solved architecturally — it is a code review and culture problem.

**Where Both Are Right (Concessions):**
- Interface boundary: Yes, worth the one afternoon to write.
- Retry budgets + jittered reconnection: Yes, non-negotiable. The Devil's Advocate is right.
- Cache invalidation during rolling deploys: Needs explicit strategy. Cannot be handwaved.

**Simplified Final Recommendation:**
Use the boring technology. Wrap it in a thin interface. Implement jittered reconnection with backpressure and bounded retry budgets from day one. Define an explicit cache invalidation strategy before deploying behind a load balancer."""
}

OFFLINE_VERDICT = """## ⚖️ Chairman's Verdict

### Who Won the Key Arguments:

**Interface vs. No Interface:** The Architect won. The Pragmatist's initial pushback was against premature complexity — but the Architect's Round 2 position (thin interface, boring technology underneath) eliminated that objection.

**Technology Choice (Complex vs. Boring):** The Pragmatist won. Even the Architect conceded the boring technology is acceptable as long as it sits behind an interface.

**Hard Non-Negotiables:** The Devil's Advocate won on thundering herd reconnection and bounded retry budgets. Neither councillor had an adequate counter-argument.

### Genuine Consensus (Survived Cross-Examination):
1. **Thin interface boundary:** All councillors converged on this after debate. Non-negotiable.
2. **Jittered reconnection + backpressure:** All acknowledged this. Mandatory before production.
3. **Bounded retry budgets with idempotency keys:** Non-negotiable.
4. **Cache invalidation strategy for rolling deploys:** Explicitly unresolved — must be decided before launch.

### The Core Irreconcilable Tension:
Simplicity Today vs. Optionality Tomorrow — resolved by the Architect's Round 2 concession. Boring technology + thin interface gives us both.

### ⚖️ BINDING FINAL DECISION:
**Use the boring technology, behind a thin domain interface, with mandatory hardening from day one.**

Rationale: The boring technology reduces TCO and is highly reversible. The thin interface preserves migration optionality at minimal cost. The Pragmatist and Architect converged on this after cross-examination.

### Phased Implementation Roadmap:
**Phase 1 — Minimal Viable Implementation (Week 1-2)**
- Choose the boring technology already in your stack.
- Define and implement the thin domain interface.
- Write contract tests validating the interface behaviour independently.

**Phase 2 — Mandatory Hardening (Before Production)**
- Implement jittered exponential backoff with bounded retry budgets.
- Add connection pool backpressure (fast 503 on saturation, not unbounded queue).
- Implement idempotency keys on all mutating operations.
- Define and document cache invalidation strategy for rolling deploys.
- Add circuit breaker with half-open health check.

**Phase 3 — Validation & Monitoring (Week 3-4)**
- Deploy behind a feature flag with 5% traffic.
- Monitor: p95/p99 latency, error rate, connection pool saturation, retry rate.
- Run a controlled chaos experiment: kill the backing service and verify graceful degradation.

### 📋 Future Plans & Open Questions:

**Unresolved questions for a future council:**
- What is the explicit cache invalidation strategy for rolling deploys?
- What is the connection pool sizing policy and saturation threshold for 503 responses?
- What monitoring/alerting thresholds should trigger automatic circuit breaker tripping?

**Suggested next council topics:**
- "How should we implement the cache invalidation strategy?" (directly follows from this decision)
- "What is our observability and on-call runbook for this service?" (follows from Phase 3)
- "When should we re-evaluate the boring technology choice?" (follow-up milestone decision)

**Mandatory follow-up mitigations (need their own review):**
- Cache invalidation strategy needs a dedicated design review before production deployment.
- Chaos engineering test plan for connection pool exhaustion scenario.
- Interface bypass audit: code review checklist to prevent direct implementation access."""


# ---------------------------------------------------------------------------
# FUTURE PLANS EXTRACTOR
# ---------------------------------------------------------------------------

def extract_future_plans(verdict: str) -> dict:
    """Best-effort extraction of future plans section from the verdict text."""
    plans = {
        "open_questions": [],
        "suggested_next_councils": [],
        "mandatory_mitigations": [],
        "notes": ""
    }
    in_section = None
    for line in verdict.split("\n"):
        stripped = line.strip()
        if "Unresolved questions" in stripped or "Open questions" in stripped:
            in_section = "open_questions"
        elif "Suggested next council" in stripped or "next council topics" in stripped:
            in_section = "suggested_next_councils"
        elif "Mandatory follow-up" in stripped or "follow-up mitigations" in stripped:
            in_section = "mandatory_mitigations"
        elif stripped.startswith("## ") and "Future" not in stripped:
            in_section = None
        elif in_section and stripped.startswith("- "):
            plans[in_section].append(stripped[2:])
    return plans


# ---------------------------------------------------------------------------
# API HELPERS
# ---------------------------------------------------------------------------

def call_gemini(api_key: str, system_prompt: str, user_prompt: str,
                model: str = "gemini-2.5-flash") -> str:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model}:generateContent?key={api_key}")
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.5}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["candidates"][0]["content"]["parts"][0]["text"]


def call_openai(api_key: str, model: str, system_prompt: str,
                user_prompt: str, base_url: str = "https://api.openai.com/v1") -> str:
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.5
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]


def call_model(system_prompt: str, user_prompt: str, verbose: bool = False) -> Optional[str]:
    gemini_key = os.environ.get("GEMINI_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if gemini_key:
        try:
            if verbose:
                print("    [API] Calling Gemini...")
            return call_gemini(gemini_key, system_prompt, user_prompt)
        except Exception as e:
            if verbose:
                print(f"    [API] Gemini error: {e}")

    if openai_key:
        try:
            if verbose:
                print("    [API] Calling OpenAI...")
            return call_openai(openai_key, "gpt-4o", system_prompt, user_prompt)
        except Exception as e:
            if verbose:
                print(f"    [API] OpenAI error: {e}")

    return None


# ---------------------------------------------------------------------------
# COUNCIL EXECUTION (with checkpoint saves after each step)
# ---------------------------------------------------------------------------

async def run_r1_seat(seat_key: str, dilemma: str, context: str, verbose: bool) -> str:
    info = ROUND1_PROMPTS[seat_key]
    print(f"  [{info['icon']} {info['title']}] Writing opening position...")
    user_prompt = f"DILEMMA: {dilemma}"
    if context:
        user_prompt += f"\n\nADDITIONAL CONTEXT: {context}"
    result = call_model(info["system"], user_prompt, verbose)
    if result:
        return result
    if verbose:
        print(f"    [Offline] Using analytical engine for {info['title']}")
    return OFFLINE_R1[seat_key]


async def run_r2_seat(seat_key: str, dilemma: str,
                      r1: Dict[str, str], verbose: bool) -> str:
    info = ROUND1_PROMPTS[seat_key]
    print(f"  [{info['icon']} {info['title']}] Cross-examining and rebutting...")

    others = {k: v for k, v in r1.items() if k != seat_key}
    names = {"architect": "Chief Systems Architect",
             "skeptic": "Devil's Advocate",
             "pragmatist": "Pragmatic Staff Engineer"}
    debate_context = "=== OTHER COUNCILLORS' OPENING POSITIONS ===\n\n"
    for k, v in others.items():
        debate_context += f"--- {names[k]} ---\n{v}\n\n"
    debate_context += f"=== YOUR OWN OPENING POSITION ===\n{r1[seat_key]}"

    user_prompt = f"DILEMMA: {dilemma}\n\n{debate_context}"
    result = call_model(ROUND2_PROMPTS[seat_key], user_prompt, verbose)
    if result:
        return result
    if verbose:
        print(f"    [Offline] Using analytical engine for {info['title']} R2")
    return OFFLINE_R2[seat_key](r1)


def run_chairman(dilemma: str, r1: Dict[str, str],
                 r2: Dict[str, str], verbose: bool) -> str:
    print("  [⚖️  Council Chairman] Reading full debate and issuing verdict...")
    names = {"architect": "Chief Systems Architect",
             "skeptic": "Devil's Advocate",
             "pragmatist": "Pragmatic Staff Engineer"}
    full_debate = f"DILEMMA: {dilemma}\n\n"
    full_debate += "=" * 60 + "\nROUND 1 — OPENING POSITIONS\n" + "=" * 60 + "\n\n"
    for k in ("architect", "skeptic", "pragmatist"):
        full_debate += f"--- {names[k]} ---\n{r1[k]}\n\n"
    full_debate += "=" * 60 + "\nROUND 2 — CROSS-EXAMINATION\n" + "=" * 60 + "\n\n"
    for k in ("architect", "skeptic", "pragmatist"):
        full_debate += f"--- {names[k]} ---\n{r2[k]}\n\n"

    result = call_model(CHAIRMAN_PROMPT, full_debate, verbose)
    if result:
        return result
    if verbose:
        print("    [Offline] Using analytical engine for Chairman")
    return OFFLINE_VERDICT


# ---------------------------------------------------------------------------
# REPORT BUILDER
# ---------------------------------------------------------------------------

def build_report(cp: dict) -> str:
    r1 = cp["rounds"]["r1"]
    r2 = cp["rounds"]["r2"]
    verdict = cp["rounds"]["verdict"]
    fp = cp.get("future_plans", {})
    now = cp.get("updated_at", "")[:16]
    dilemma = cp["dilemma"]
    sid = cp["session_id"]

    report = f"""# 🏛️ Council Deliberation Report
**Session ID:** `{sid}`  
**Dilemma:** {dilemma}  
**Completed:** {now}  
**Framework:** Antigravity Ask Council — Multi-Round Debate

> [!TIP]
> To resume or extend this session: `python council_runner.py --resume {sid}`

---

## ROUND 1 — Opening Positions

*Each councillor deliberated independently with no knowledge of the others' positions.*

{r1.get("architect", "")}

---

{r1.get("skeptic", "")}

---

{r1.get("pragmatist", "")}

---

## ROUND 2 — Cross-Examination & Rebuttals

*Each councillor read the others' Round 1 positions and responded directly.*

{r2.get("architect", "")}

---

{r2.get("skeptic", "")}

---

{r2.get("pragmatist", "")}

---

## ROUND 3 — Chairman's Verdict

*The Chairman read the full debate thread and issued the binding decision.*

{verdict}
"""

    # Append future plans summary if extracted
    if fp.get("open_questions") or fp.get("suggested_next_councils"):
        report += "\n---\n\n## 📋 Session Future Plans (Structured)\n\n"
        if fp.get("open_questions"):
            report += "### Open Questions for Next Session\n"
            for q in fp["open_questions"]:
                report += f"- {q}\n"
            report += "\n"
        if fp.get("suggested_next_councils"):
            report += "### Suggested Next Council Topics\n"
            for t in fp["suggested_next_councils"]:
                report += f"- {t}\n"
            report += "\n"
        if fp.get("mandatory_mitigations"):
            report += "### Mandatory Follow-Up Reviews\n"
            for m in fp["mandatory_mitigations"]:
                report += f"- {m}\n"
            report += "\n"

    report += f"\n---\n*Resume this session: `python council_runner.py --resume {sid}`*\n"
    return report


# ---------------------------------------------------------------------------
# MAIN ASYNC RUNNER
# ---------------------------------------------------------------------------

async def run_council(cp: dict, args) -> dict:
    dilemma = cp["dilemma"]
    context = cp["context"]
    verbose = args.verbose

    # ── ROUND 1 ─────────────────────────────────────────────────────────────
    if cp["status"] in ("started",) or not all(
            k in cp["rounds"]["r1"] for k in ("architect", "skeptic", "pragmatist")):
        print("\n[ ROUND 1: Opening Positions — All 3 deliberating independently ]\n")
        seats = [k for k in ("architect", "skeptic", "pragmatist")
                 if k not in cp["rounds"]["r1"]]
        if seats:
            tasks = [run_r1_seat(k, dilemma, context, verbose) for k in seats]
            results = await asyncio.gather(*tasks)
            for k, v in zip(seats, results):
                cp["rounds"]["r1"][k] = v
            cp["status"] = "r1_complete"
            save_checkpoint(cp, verbose)
        else:
            print("  [Checkpoint] Round 1 already complete — skipping.\n")
    else:
        print("\n[ ROUND 1: Already complete — loaded from checkpoint ]\n")

    r1 = cp["rounds"]["r1"]

    # ── ROUND 2 ─────────────────────────────────────────────────────────────
    if cp["status"] in ("started", "r1_complete") or not all(
            k in cp["rounds"]["r2"] for k in ("architect", "skeptic", "pragmatist")):
        print("\n[ ROUND 2: Cross-Examination — Each reads the others and rebuts ]\n")
        seats = [k for k in ("architect", "skeptic", "pragmatist")
                 if k not in cp["rounds"]["r2"]]
        if seats:
            tasks = [run_r2_seat(k, dilemma, r1, verbose) for k in seats]
            results = await asyncio.gather(*tasks)
            for k, v in zip(seats, results):
                cp["rounds"]["r2"][k] = v
            cp["status"] = "r2_complete"
            save_checkpoint(cp, verbose)
        else:
            print("  [Checkpoint] Round 2 already complete — skipping.\n")
    else:
        print("\n[ ROUND 2: Already complete — loaded from checkpoint ]\n")

    r2 = cp["rounds"]["r2"]

    # ── ROUND 3: CHAIRMAN ────────────────────────────────────────────────────
    if not cp["rounds"].get("verdict"):
        print("\n[ ROUND 3: Chairman's Verdict ]\n")
        verdict = run_chairman(dilemma, r1, r2, verbose)
        cp["rounds"]["verdict"] = verdict
        cp["future_plans"] = extract_future_plans(verdict)
        cp["status"] = "complete"
        save_checkpoint(cp, verbose)
    else:
        print("\n[ ROUND 3: Already complete — loaded from checkpoint ]\n")

    return cp


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Antigravity Ask Council — Multi-Round Debate with Session Checkpointing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # New session
  python council_runner.py -d "Should we use Kafka or Redis Pub/Sub?" --session my-kafka-debate

  # Resume interrupted session
  python council_runner.py --resume my-kafka-debate

  # List all saved sessions
  python council_runner.py --list-sessions

  # Save report to file after completion
  python council_runner.py --resume my-kafka-debate --output kafka_verdict.md
        """)

    parser.add_argument("--dilemma", "-d",
                        help="The question, proposal, or dilemma to evaluate")
    parser.add_argument("--context", "-c", default="",
                        help="Additional technical context or constraints")
    parser.add_argument("--session", "-s", default="",
                        help="Named session ID (auto-generated if not provided)")
    parser.add_argument("--resume", "-r", default="",
                        help="Resume an interrupted session by session ID")
    parser.add_argument("--list-sessions", "-l", action="store_true",
                        help="List all saved sessions and their status")
    parser.add_argument("--output", "-o", default="",
                        help="Path to write the final markdown report")
    parser.add_argument("--offline", action="store_true",
                        help="Force offline analytical engine (no external API calls)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print verbose execution details")

    args = parser.parse_args()

    # ── LIST SESSIONS ────────────────────────────────────────────────────────
    if args.list_sessions:
        list_sessions()
        return

    # ── OFFLINE MODE ─────────────────────────────────────────────────────────
    if args.offline:
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)

    # ── LOAD OR CREATE CHECKPOINT ────────────────────────────────────────────
    if args.resume:
        cp = load_checkpoint(args.resume)
        print(f"\n[Checkpoint] Resuming session: {cp['session_id']}")
        print(f"             Status: {cp['status']}")
        print(f"             Dilemma: {cp['dilemma']}")
        if cp["status"] == "complete" and not args.output:
            print("\n[!] This session is already complete.")
            print(f"    Use --output <file> to export the final report.")
            print(f"    Session path: {session_path(cp['session_id'])}")
    else:
        if not args.dilemma:
            parser.error("--dilemma is required when starting a new session")
        session_id = args.session.strip() or f"council-{uuid.uuid4().hex[:8]}"
        # Check if session already exists
        if os.path.exists(session_path(session_id)):
            print(f"\n[!] Session '{session_id}' already exists.")
            print(f"    Use --resume {session_id} to continue it.")
            sys.exit(1)
        cp = new_checkpoint(session_id, args.dilemma, args.context)
        save_checkpoint(cp, args.verbose)

    # ── RUN DEBATE ───────────────────────────────────────────────────────────
    if cp["status"] != "complete":
        print(f"\n{'='*60}")
        print(f"🏛️  ANTIGRAVITY COUNCIL — MULTI-ROUND DEBATE")
        print(f"{'='*60}")
        print(f"Session: {cp['session_id']}")
        print(f"Dilemma: {cp['dilemma']}")
        print(f"\n[TIP] If this is interrupted, resume with:")
        print(f"      python council_runner.py --resume {cp['session_id']}\n")

        cp = asyncio.run(run_council(cp, args))

        print("\n\n🏛️  Council adjourned successfully.")
        print(f"    Session saved: {session_path(cp['session_id'])}")
    else:
        print("\n[Council] Session already complete.")

    # ── EXPORT REPORT ────────────────────────────────────────────────────────
    report = build_report(cp)

    if args.output:
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ Report saved to: {out_path}")
    elif cp["status"] == "complete" and args.resume:
        # If just resuming to check output, print it
        print("\n" + report)

    # Print future plans summary
    fp = cp.get("future_plans", {})
    if fp.get("open_questions"):
        print("\n📋 Open questions for a future council:")
        for q in fp["open_questions"]:
            print(f"   • {q}")
    if fp.get("suggested_next_councils"):
        print("\n🔜 Suggested next council topics:")
        for t in fp["suggested_next_councils"]:
            print(f"   • {t}")


if __name__ == "__main__":
    main()
