# Ask Council: Execution Modes

The Ask Council framework supports two primary execution patterns depending on your environment, workflow, and API keys:

---

## Mode 1: Native Antigravity Subagents (Recommended / Zero Config)

This mode runs natively inside the Antigravity desktop or CLI using the agent's built-in subagent orchestration (`invoke_subagent`).

### How It Works:
1. When you ask Antigravity to consult the council, the primary agent parses your question.
2. The agent issues a single `invoke_subagent` call containing an array of 3 or 4 subagents:
   ```json
   {
     "Subagents": [
       {
         "Role": "Chief Systems Architect",
         "Model": "pro",
         "TypeName": "self",
         "Prompt": "<Architect persona prompt + user question>"
       },
       {
         "Role": "Devil's Advocate / Red Teamer",
         "Model": "pro",
         "TypeName": "self",
         "Prompt": "<Skeptic persona prompt + user question>"
       },
       {
         "Role": "Pragmatic Staff Engineer",
         "Model": "pro",
         "TypeName": "self",
         "Prompt": "<Pragmatist persona prompt + user question>"
       }
     ]
   }
   ```
3. All three subagents execute concurrently in the background.
4. When they finish, Antigravity receives their messages automatically.
5. The primary agent assumes the role of **Council Chairman**, analyzes the positions, drafts the deliberation artifact, and delivers the verdict.

### Advantages:
- **Zero Configuration**: Uses your active Antigravity session. No API keys, subscriptions, or external network configurations needed.
- **Deep Codebase Access**: Subagents can inspect your project files, workspace rules, and git repository directly.
- **Artifact Integration**: Directly generates native Antigravity Markdown artifacts (`council_deliberation.md`) viewable in the Antigravity artifact drawer.

---

## Mode 2: Multi-Model External Runner (`council_runner.py`)

If you want cross-model ensemble consultation (e.g. comparing outputs from Anthropic Claude 3.7 Sonnet, OpenAI GPT-4o, and Google Gemini 2.5/3 Pro), you can use the companion Python script located in `scripts/council_runner.py`.

### How It Works:
1. The script inspects your environment for available API keys:
   - `GEMINI_API_KEY` (Gemini models via `google-genai` or direct REST)
   - `ANTHROPIC_API_KEY` (Claude via `anthropic` or REST)
   - `OPENAI_API_KEY` (GPT models via `openai` or REST)
   - `OPENROUTER_API_KEY` (Unified access to all models)
2. Each model is assigned a specific council persona or asked to independently review the problem.
3. The responses are collected concurrently via `asyncio`.
4. A chairman model (or local heuristics) synthesizes the answers into a unified report.

### Running the Script:
```bash
# Basic run with problem statement
python scripts/council_runner.py --dilemma "Should we switch from PostgreSQL to MongoDB for our chat message history?"

# Specify output file
python scripts/council_runner.py --dilemma "REST vs gRPC for internal microservices" --output council_verdict.md

# Offline / Simulation mode (tests council pipeline without API keys)
python scripts/council_runner.py --dilemma "Should we introduce a message broker?" --offline
```
