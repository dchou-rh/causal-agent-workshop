# Workshop Guide

**Build an Intelligence Agent, Not a Chatbot**

> *Not what happened. Why it happened. What happens next.*

A 90-minute hands-on workshop on building agents that reason about data — not just repeat it.

---

## Who this is for

You should be comfortable writing basic Python (functions, dictionaries, imports) and running commands in a terminal. You do **not** need a computer science degree, statistics coursework, or prior experience building AI agents.

**Before you begin:** Complete setup in the [README](../README.md). You need Cursor, API keys, and a successful run of `verify.py`.

---

## What you will have at the end

A small agent that:

1. **Pulls real data** from GitHub (not guesses)
2. **Adds context** to every metric (benchmarks, trends, flags)
3. **Reasons causally** with evidence tiers and alternative explanations
4. **Packages as a portable Agent Skill** for Cursor and other tools

---

## Schedule at a glance

| Time | ADLC phase | What you do |
|------|------------|-------------|
| 0:00–0:05 | **Prepare** | Run setup check |
| 0:05–0:15 | **Plan** | Learn the data-intelligence boundary |
| 0:15–0:35 | **Build** | Implement `get_repo_health` |
| 0:35–0:55 | **Build** | Implement `analyze_causal_patterns` |
| 0:55–1:10 | **Test & orchestrate** | Wire tools to Groq; compare agents |
| 1:10–1:22 | **Deploy** | Package as an Agent Skill |
| 1:22–1:30 | **Govern** | Wrap-up and discussion |

**Running behind?** Focus on Part 3 — that is where the agent comes alive. Parts 1–2 are the foundation; Part 4 is packaging what you already built.

---

## ADLC: How this workshop is structured

**ADLC** (Agent Development Lifecycle) is how teams build AI agents responsibly — not as one-shot demos, but as systems you can trust, test, and improve.

Traditional software (SDLC) ships code with predictable outputs. Agents are different: the same prompt can produce different answers. ADLC adds practices for that uncertainty.

In 90 minutes we touch five ADLC ideas you can use on any agent project:

| ADLC principle | What it means here |
|----------------|-------------------|
| **Plan before you prompt** | Define what the agent should do, what data it needs, and what "good" looks like |
| **Separate data from judgment** | Python returns facts; the LLM interprets them |
| **Build guardrails in** | System prompts, tool boundaries, evidence tiers — not hope the model behaves |
| **Evaluate, don't just demo** | Compare your causal agent to a naive agent with no tools |
| **Package for reuse** | Ship tools + rules together as an Agent Skill |

Each part below calls out which ADLC phase you are in and what deliverable you are producing.

---

## Prepare: Setup check (5 min)

**ADLC phase:** Prepare — confirm your environment works before building.

From the project root:

```bash
uv run --directory src python verify.py
```

**Success looks like:**

```
GitHub OK: pallets/flask (… stars)
Groq OK: ready
```

The star count can differ. Both lines must say `OK`.

Open `src/tools.py`. You will implement the functions marked `NotImplementedError` during Parts 1 and 2.

**Stuck?** See [README troubleshooting](../README.md#troubleshooting).

---

## Plan: The data-intelligence boundary (10 min)

**ADLC phase:** Plan — define the problem, scope, and success criteria.

*No coding in this section. Follow along and discuss.*

### The core question

Most "AI agent" tutorials connect an LLM to an API and stop. That produces a **chatbot** — it talks confidently but may invent numbers.

This workshop builds an **intelligence agent** — one that grounds every claim in retrieved data and states how confident it should be.

### Where to draw the line

| Data layer (your Python code) | Intelligence layer (the LLM) |
|---|---|
| Numbers, flags, z-scores | What those numbers mean for the user |
| Historical benchmarks | Whether a deviation matters |
| Causal pathway evidence | Which explanation is most plausible |
| Methodology notes ("Tier 2 pattern match") | Narrative synthesis |

**Rule of thumb:** If it could be wrong in a spreadsheet, it belongs in Python. If it requires judgment, it belongs in the LLM.

### ADLC planning checklist (for this agent)

Before you write code, you should be able to answer:

- [ ] **Problem:** Help someone evaluate open-source project health on GitHub
- [ ] **Inputs:** Repository owner + name (e.g. `pallets/flask`)
- [ ] **Outputs:** Structured metrics, causal evidence, narrative briefing
- [ ] **Success:** Agent never quotes a metric it did not retrieve; causal claims include evidence tier + alternative

---

## Build — Part 1: Data tools with context (20 min)

**ADLC phase:** Build — implement the data layer with clear boundaries.

**File:** `src/tools.py`  
**Function:** `get_repo_health(owner, repo)`

### Why this matters

"This repo had 47 commits last month" is useless without context. Your job is to return **numbers plus benchmarks** so the LLM never has to guess.

### Step-by-step

#### 1. Fetch the repository

The GitHub client `gh` is already set up. Get the repo object:

```python
r = gh.get_repo(f"{owner}/{repo}")
now = datetime.now(timezone.utc)
```

#### 2. Get weekly commit counts

```python
stats = r.get_stats_commit_activity()
weekly_commits = [week.total for week in stats] if stats else []
```

> **First request may return empty data** while GitHub computes stats. Wait 5 seconds and run your checkpoint again.

#### 3. Compute recent vs. historical activity

| Variable | How to calculate |
|----------|------------------|
| `recent_avg` | Mean of the last 4 weeks |
| `hist_mean` | Mean of all weeks |
| `hist_stdev` | Standard deviation (use `1.0` if fewer than 2 weeks) |
| `z_score` | `(recent_avg - hist_mean) / hist_stdev` |

**Z-score in plain English:** How unusual is recent activity compared to this repo's own history? A z-score of -1.5 means "noticeably below normal for this project."

#### 4. Contributor concentration ("bus factor")

```python
contributors = list(r.get_stats_contributors() or [])
```

Calculate `top_contributor_share` — what fraction of commits came from the single busiest contributor?

#### 5. Issue health (last 90 days)

Fetch issues, **exclude pull requests**, count open vs. closed. Compute `close_ratio`.

#### 6. Return a dictionary — facts only

Your return value must include:

```
repository, stars, forks
metrics.commit_activity     → recent_weekly_avg, historical_weekly_avg, z_score, trend, weeks_observed
metrics.contributor_concentration → total_contributors, top_contributor_share
metrics.issue_health        → open_issues_90d, closed_issues_90d, close_ratio
indicator_flags           → is_active, is_declining, has_bus_factor_risk, has_issue_backlog
retrieved_at                → ISO timestamp
```

**Indicator flags are boolean facts** — not opinions:

| Flag | True when… |
|------|------------|
| `is_active` | Recent weekly average > 0 |
| `is_declining` | z-score < -1.0 |
| `has_bus_factor_risk` | Top contributor share > 50% |
| `has_issue_backlog` | More open than closed issues |

Do **not** return words like "unhealthy", "concerning", or "you should switch libraries."

#### 7. Implement `_classify_trend(weekly)`

Split the weekly list in half. Compare averages. Return:

| Condition | Label |
|-----------|-------|
| Fewer than 8 weeks | `insufficient_data` |
| Second half / first half > 1.2 | `accelerating` |
| Ratio > 0.9 | `stable` |
| Ratio > 0.6 | `slowing` |
| Otherwise | `declining` |

### Checkpoint ✓

```bash
uv run --directory src python -c "from tools import get_repo_health; import json; print(json.dumps(get_repo_health('pallets', 'flask'), indent=2, default=str))"
```

**Success:** JSON output with `metrics`, `indicator_flags`, and a numeric `z_score`.

### ADLC build note

You just defined the **contract** for your data layer. Every consumer of `get_repo_health` — different prompts, different users — gets the same facts. That is how you build agents that scale beyond a single demo.

---

## Build — Part 2: Causal reasoning (20 min)

**ADLC phase:** Build — add structured evidence the LLM can reason over.

**File:** `src/tools.py` (same file)  
**Functions:** `analyze_causal_patterns`, `_get_alternative`

### Why correlation is not enough

Part 1 tells you *what* is happening. Causal reasoning asks *why* — and requires honesty about how strong the evidence is.

### Pearl's ladder (simplified)

| Level | Question | Example |
|-------|----------|---------|
| Association | What is? | "Commits declined" |
| Intervention | What if we act? | "What if we added a maintainer?" |
| Counterfactual | Why did it happen? | "Did maintainer burnout cause the decline?" |

This workshop operates at **pattern matching** (Tier 2) — not proof.

### Step-by-step

#### 1. Define `CAUSAL_PATHWAYS`

A list of dicts. Each pathway describes a known cause-effect chain in open-source projects.

Build two pathways:

**Pathway 001 — Maintainer Departure Cascade**

Maintainer stops contributing → reviews slow → fewer external contributors

**Pathway 002 — Release Drought**

No release in 90+ days → adoption stalls → fork activity rises

Each pathway needs: `id`, `name`, `mechanism`, `nodes`, `detection`, `evidence_tier` (use `2`), `confidence_base` (e.g. `0.55` and `0.45`).

#### 2. Implement `analyze_causal_patterns(owner, repo)`

For each pathway, check what you can observe in the data:

| Pathway | What to check |
|---------|---------------|
| 001 | Top contributor's last active week; unique contributors this quarter vs. prior quarter |
| 002 | Days since last release |

For each pathway, build a result dict with:

- `observations` — per-node detected/not + detail string
- `nodes_detected`, `nodes_checked`, `match_strength`
- `adjusted_confidence` — base confidence × match strength
- `alternative_explanation` — from `_get_alternative()`

**Return evidence, not conclusions.** Do not pick a "winner" pathway.

#### 3. Implement `_get_alternative(pathway_id)`

Every causal claim needs a competing explanation. Examples:

- Pathway 001: seasonal slowdown (holidays, summer)
- Pathway 002: intentional stability in a mature project

### Evidence tiers (use these in Part 3)

| Tier | Strength | How to phrase it |
|------|----------|------------------|
| 1 | Temporal sequence | "Following X, we observed Y…" |
| 2 | Pattern match | "This matches a known pattern…" |
| 3 | Peer comparison | "Similar projects without X didn't show Y…" |
| 4 | Statistical test | "Across N projects, X predicts Y (p < 0.05)…" |

Your tools are **Tier 2**. The LLM must say so.

### Checkpoint ✓

```bash
uv run --directory src python -c "from tools import analyze_causal_patterns; import json; print(json.dumps(analyze_causal_patterns('pallets', 'flask'), indent=2, default=str))"
```

**Success:** `pathways_checked: 2` with `observations` for each pathway.

### ADLC build note

You are **building guardrails into the data layer** — alternatives and evidence tiers are not optional niceties. They prevent overconfident agents.

---

## Test & orchestrate — Part 3: Wire tools to Groq (15 min)

**ADLC phase:** Test & orchestrate — connect tools to the LLM and evaluate behavior.

**File:** Create `src/agent.py`

### What you are building

An **agent loop:**

```
User question → LLM decides which tools to call → your Python runs → LLM synthesizes answer
```

Plus a **naive agent** with no tools — for comparison. This is your evaluation harness.

### Step-by-step

#### 1. Create the file with imports

```python
import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq

from tools import get_repo_health, analyze_causal_patterns

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
```

#### 2. Define `TOOLS` — the LLM's menu

Two function schemas (Groq function-calling format). Each needs:

- `name` — must match your Python function name
- `description` — what it returns **and** what it does **not** return
- `parameters` — `owner` and `repo` (both required strings)

**ADLC tip:** Tool descriptions are guardrails. "Does NOT return opinions" keeps the data-intelligence boundary intact.

#### 3. Map names to functions

```python
TOOL_FUNCTIONS = {
    "get_repo_health": get_repo_health,
    "analyze_causal_patterns": analyze_causal_patterns,
}
```

#### 4. Write `SYSTEM_PROMPT` — your agent's rules

Include these rules (in your own words):

1. Always call `get_repo_health` first
2. If flags are concerning, call `analyze_causal_patterns`
3. Never quote a number without its benchmark context
4. State evidence tier for every causal claim
5. Acknowledge at least one alternative explanation
6. Use hedged language for Tier 1–2 ("Based on observed patterns…")
7. Write a narrative briefing, not a bullet dump

#### 5. Implement `run_agent(user_message)`

```
loop:
    send messages to Groq with tools=TOOLS
    if model requests tool calls:
        run each Python function
        append results to messages
        continue loop
    else:
        return the text response
```

Use model: `llama-3.3-70b-versatile`

Print each tool call so you can see what happened:

```python
print(f"  [Calling {fn_name}({fn_args})]")
```

#### 6. Implement `run_naive_agent(user_message)`

Same model. System prompt: `"You are a helpful assistant."` No tools.

#### 7. Add `if __name__ == "__main__"`

Run both agents on the same query. Default: `"Analyze the health of the pallets/flask repository."`

### Checkpoint ✓

```bash
uv run --directory src python agent.py
```

**Success:**

- Terminal shows `[Calling get_repo_health(...)]`
- Causal agent output cites real metrics with context
- Naive agent invents or guesses numbers — **that is the point**

### Try other repos

```bash
uv run --directory src python agent.py "Analyze the health of facebook/react"
uv run --directory src python agent.py "Should I contribute to psf/requests?"
```

### ADLC evaluation note

You just ran a **behavioral comparison** — the simplest form of agent evaluation. In production you would automate this with test cases and score outputs. Here, reading both side by side is enough to see why tools + rules matter.

---

## Deploy — Part 4: Package as an Agent Skill (12 min)

**ADLC phase:** Deploy — make your agent portable and reusable.

You will package your tools and reasoning rules as an [Agent Skill](https://agentskills.io) — a folder any compatible editor can load.

### Folder structure

```bash
mkdir -p .cursor/skills/repo-health-analyst/scripts
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path .cursor/skills/repo-health-analyst/scripts
```

### Step-by-step

#### 1. Create `SKILL.md`

YAML frontmatter at the top:

```yaml
---
name: repo-health-analyst
description: >
  Analyze GitHub repository health using causal reasoning. Use when asked to
  evaluate project health, maintenance, contributor risk, or adoption decisions.
compatibility: Requires Python 3.11+, uv, GITHUB_TOKEN, GROQ_API_KEY.
---
```

Then write instructions for:

- How to run health and causal scripts
- Interpretation rules (no naked numbers, evidence tiers, alternatives)
- Output format: Overview → Health Assessment → Causal Analysis → Assessment

The `description` field is how Cursor decides when to activate your skill — write it carefully.

#### 2. Copy `src/tools.py` to the skill

```bash
cp src/tools.py .cursor/skills/repo-health-analyst/scripts/tools.py
```

Windows: `Copy-Item src/tools.py .cursor/skills/repo-health-analyst/scripts/tools.py`

#### 3. Add a CLI to the skill's `tools.py`

At the bottom of the copied file:

```python
if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 4:
        print("Usage: tools.py <health|causal> <owner> <repo>")
        sys.exit(1)

    command, owner, repo = sys.argv[1], sys.argv[2], sys.argv[3]

    if command == "health":
        result = get_repo_health(owner, repo)
    elif command == "causal":
        result = analyze_causal_patterns(owner, repo)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))
```

#### 4. Test the scripts

```bash
uv run python .cursor/skills/repo-health-analyst/scripts/tools.py health pallets flask
uv run python .cursor/skills/repo-health-analyst/scripts/tools.py causal pallets flask
```

#### 5. Test in Cursor

Open chat (**Cmd+L** / **Ctrl+L**) and ask:

> Analyze the health of pallets/flask

Cursor should load your skill, run your scripts, and follow your rules.

### What you packaged

| Layer | Artifact |
|-------|----------|
| Capability | `scripts/tools.py` |
| Rules | `SKILL.md` |
| Runtime | Cursor (or any Agent Skills-compatible tool) |

You now have **two deployments** of the same logic:

1. `src/agent.py` — standalone Groq agent
2. `.cursor/skills/...` — editor-integrated skill

### ADLC deploy note

Version your skill (`metadata.version` in frontmatter). When you change thresholds or rules, bump the version — same discipline as any deployable artifact.

---

## Govern: Wrap-up (8 min)

**ADLC phase:** Govern — reflect on what you built and what you would monitor in production.

### Run the comparison one more time

```bash
uv run --directory src python agent.py
```

| | Causal agent | Naive agent |
|---|---|---|
| Data source | GitHub API | None (hallucination risk) |
| Context | z-scores, benchmarks | Raw numbers or guesses |
| Causal claims | Tier + alternatives | Unqualified assertions |

### Discussion questions

1. **The boundary test.** `is_declining` uses z-score < -1.0. Is the threshold a fact or a judgment? Where does the line fall?

2. **Evidence tiers.** What data would you need to move from Tier 2 (pattern) to Tier 3 (peer comparison)?

3. **Prompt sensitivity.** Remove one rule from `SYSTEM_PROMPT` and re-run. How much intelligence came from tools vs. instructions?

4. **Same data, different users.** How would you change the prompt (not the tools) for a CTO vs. a new contributor?

### What you would add for production (ADLC govern)

In a real deployment you would also plan for:

- **Monitoring** — track tool call failures, latency, token cost
- **Evaluation suite** — automated test repos with expected flag values
- **Access control** — least-privilege GitHub tokens
- **Drift** — re-check when GitHub API behavior or model versions change

This workshop gives you the foundation. ADLC is the discipline for everything after the demo.

---

## Reference card

### Project structure (when complete)

```
causal-agent-workshop/
├── README.md
├── docs/workshop-guide.md
├── src/
│   ├── verify.py
│   ├── tools.py
│   └── agent.py
└── .cursor/skills/repo-health-analyst/
    ├── SKILL.md
    └── scripts/tools.py
```

### Commands

```bash
uv run --directory src python verify.py
uv run --directory src python agent.py
uv run --directory src python agent.py "Analyze the health of facebook/react"
```

### The five rules

1. Never present a number without reference context.
2. Never let a data function return opinions.
3. Every causal claim states its evidence tier.
4. Every causal claim acknowledges an alternative.
5. The LLM judges. The functions fact.

---

## Going further

- **Peer cohort tool** — z-scores against similar repos, not just self-history
- **Counterfactual scenarios** — "what if we add a maintainer?" with a status-quo baseline
- **Multi-persona prompts** — same tools, different system prompts per audience
- **Publish your skill** — share on GitHub for others to clone

---

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
