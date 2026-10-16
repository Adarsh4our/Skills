# Antigravity & Agent Skills Collection

A comprehensive collection of production-ready skills, agent workflows, and developer tools for [Google Antigravity](https://antigravity.google) and compatible AI coding assistants (Claude Code, Cursor, Codex CLI, Gemini CLI).

---

## 🚀 Ubuntu / Linux Setup Guide

To install and activate all skills on your Ubuntu machine:

### Option 1: Direct Global Config Clone (Recommended)
Clone this repository directly into Antigravity's global skills discovery directory:

```bash
mkdir -p ~/.gemini/config
git clone https://github.com/Adarsh4our/Skills.git ~/.gemini/config/skills
```

If you also use tools that discover skills via the universal `~/.agents/skills` path:
```bash
mkdir -p ~/.agents
ln -s ~/.gemini/config/skills ~/.agents/skills
```

---

### Option 2: Clone & Copy / Link
Clone the repository anywhere (e.g. `~/Skills`) and copy into your configuration paths:

```bash
git clone https://github.com/Adarsh4our/Skills.git ~/Skills

# Create directories
mkdir -p ~/.gemini/config/skills
mkdir -p ~/.agents/skills

# Copy skills
cp -r ~/Skills/* ~/.gemini/config/skills/
cp -r ~/Skills/* ~/.agents/skills/
```

---

### 📦 Optional Prerequisite CLI Tools (for Skills with CLI Engines)

Certain skills leverage underlying CLI utilities for AST parsing, multi-provider routing, or documentation lookups. To get full functionality on Ubuntu:

```bash
# 1. Universal Skills CLI & Context7
npm install -g skills ctx7

# 2. OmniRoute (Local Multi-Provider AI Gateway)
npm install -g omniroute

# 3. Graphify (Codebase AST & Knowledge Graph Engine)
pip install graphifyy
```

---

## 📚 Skill Catalog

| Skill Name | Category | Description |
| :--- | :--- | :--- |
| **`archify`** | Architecture & Design | Turns codebases or system designs into interactive, verifiable HTML/SVG architecture, sequence, and workflow diagrams. |
| **`ask_council`** | Decision Making | Convenes a multi-agent council of specialized AI personas (Architect, Red Teamer, Staff Engineer, Chairman) for deep technical debates. |
| **`context7`** | Documentation | Retrieves live, version-accurate documentation and code examples from official sources via Context7 API. |
| **`context7-cli`** | Documentation | Direct integration with the `ctx7` CLI tool to query library references and API specs. |
| **`context7-mcp`** | Protocol & Tools | Model Context Protocol (MCP) server configuration and workflow for Context7. |
| **`deploy-to-vercel`** | Deployment | Automated deployment workflows, preview builds, and environment setups on Vercel. |
| **`design-md`** | UI/UX & Markdown | Guidelines and tooling for designing and formatting modern UI documents and specs. |
| **`enhance-prompt`** | Prompt Engineering | Refines and optimizes user prompts for maximum agent reasoning and code generation quality. |
| **`find-docs`** | Documentation | Dynamic documentation and API reference fetcher across modern frameworks (Next.js, React, Supabase, Tailwind, etc.). |
| **`find-skills`** | Agent Utility | Searches and discovers public agent skills from the open skills registry. |
| **`graphify`** | Codebase Analysis | Extracts local AST call-graphs, dependencies, and Leiden community clusters into a queryable knowledge graph. |
| **`gravitas`** | Reliability Runtime | Enforces scoped reconnaissance, ground-before-mutating rules, and evidence-backed verification before claiming tasks complete. |
| **`gravitas-highstakes`**| Safety & Governance | Mandatory checkpointing, adversarial critique, and dry-run verification for irreversible changes (migrations, auth, deletions). |
| **`gravitas-python`** | Language Specific | Python-specific verification patterns using `mypy --strict`, `ruff`, and `pytest`. |
| **`gravitas-typescript`**| Language Specific | TypeScript-specific verification patterns using strict `tsc`, linting, and `vitest`/`jest`. |
| **`inter-iit-ps`** | Research & Hackathons | Specialized problem statement analysis and solution proposal generator for Inter-IIT Tech Meet challenges. |
| **`markdown_handbook_formatter`** | Utility | Cleans and formats raw Markdown handbooks, double-spaced slides, and ASCII diagrams into structured documentation. |
| **`ponytail`** | Engineering Philosophy | Enforces minimalist, pragmatic YAGNI development — favors standard libraries, native features, and minimum code over bloat. |
| **`ponytail-audit`** | Code Audit | Quality audit of codebases: identifies bugs, security gaps, performance bottlenecks, and dead code. |
| **`ponytail-debt`** | Tech Debt | Scans and categorizes deferred shortcuts and architectural debt across repositories. |
| **`ponytail-gain`** | Analytics | Benchmarks and displays measured code reduction and performance savings. |
| **`ponytail-help`** | Quick Reference | Reference guide and command syntax for Ponytail intensity modes (`lite`, `full`, `ultra`). |
| **`ponytail-review`** | Code Review | Pragmatic code reviewer evaluating logic correctness, safety, and eliminating over-engineering. |
| **`problem-statement`** | Technical Research | Deep-dive requirement analysis, baseline architectures, and proposal drafting for hackathons and RFPs. |
| **`react-components`** | Frontend | Best practices for modular React component design, state management, and accessibility. |
| **`remotion`** | Video & Animation | Programmatic video creation and animation using React and Remotion. |
| **`shadcn-ui`** | UI Components | Component generation, styling, and integration patterns with Tailwind CSS and Radix UI. |
| **`stitch-design`** | Visual Design | Component and interface layout composition tools. |
| **`stitch-loop`** | Visual Design | Iterative design loop helper for agent UI synthesis. |
| **`user-profile`** | Personalized Context | Contextual behavioral profile, cognitive preferences, and project background for Adarsh Singh. |
| **`vercel-cli-with-tokens`** | Cloud & DevOps | Token-authenticated Vercel CLI deployment and project configuration. |
| **`vercel-composition-patterns`** | React Architecture | Scalable React composition patterns, compound components, and render-prop architectures. |
| **`vercel-optimize`** | Performance & Cost | Audits and optimizes Vercel deployments (Function Invocations, build minutes, data transfer, Core Web Vitals). |
| **`vercel-react-best-practices`** | React Performance | Performance optimization rules from Vercel Engineering (memoization, bundle sizing, streaming SSR). |
| **`vercel-react-native-skills`** | Mobile Engineering | Performant mobile component patterns for React Native and Expo. |
| **`vercel-react-view-transitions`** | Animation | Native-feeling page and layout animations using React View Transition APIs. |
| **`web-design-guidelines`** | UI/UX Compliance | Audits UI code against modern Web Interface Guidelines for usability and accessibility. |
| **`writing-guidelines`** | Prose & Documentation | Style guide and tone checker for technical documentation and developer guides. |

---

## 📄 License

MIT / Open Source — Individual skill licenses are preserved within their respective skill definitions.
