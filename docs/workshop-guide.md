# Workshop Guide

**Build an Intelligence Agent, Not a Chatbot**

> *Not what happened. Why it happened. What happens next.*

A 90-minute hands-on workshop on building agents that reason about data — not just repeat it.

---

## Why causal reasoning?

Most agent demos stop at retrieval: pull a metric, summarize it, call it intelligence. In practice, that leaves users with the same question they started with — *so what?*

Effective decision-support agents are built around a simple idea: users need three things — not one:

| Question | What users actually need |
|----------|--------------------------|
| **What happened?** | Accurate data |
| **Why did it happen?** | Causal context — plausible mechanisms, not just correlated trends |
| **What happens next?** | Grounded judgment a human can act on |

That framing — *not what happened, but why it happened and what happens next* — is why this workshop goes beyond wiring an LLM to an API.

### How this differs from traditional machine learning

Traditional ML is built to **predict** — given inputs, produce a score or label trained on historical examples. That works well when you have lots of labeled data, a stable problem, and users who only need the prediction itself.

| | Traditional ML | This workshop's approach |
|---|---|---|
| **Primary output** | A score or class ("73% churn risk") | Structured facts + narrative reasoning |
| **Training** | Collect data, engineer features, train, validate, deploy | No model training — you write tools and prompts |
| **"Why?"** | Often opaque; explainability is a separate project | Designed in: baselines, pathways, evidence tiers, alternatives |
| **Causation** | Usually learns correlation; true causality needs extra methods and data | Explicit causal templates + honest confidence labels |
| **Adaptability** | New questions often mean new features or retraining | Same tools; the LLM adapts answers to the user's question |
| **Best at** | High-volume pattern matching at scale | Interactive analysis where context and explanation matter |

Neither replaces the other. Production systems often use **both**: ML for scoring at scale, agents for interpretation, investigation, and communication. The mistake is treating an LLM chatbot as a substitute for either — it has no trained model of your domain and no structured evidence unless you build that layer.

This workshop focuses on that missing layer: **tools that return auditable facts**, plus **reasoning rules** that force the agent to contextualize metrics, separate correlation from mechanism, and admit uncertainty.

### What we learned building intelligence agents (not chatbots)

These patterns show up whenever an agent has to support real decisions. They are not domain-specific tricks; they are design choices:

1. **Metrics without baselines are noise.** A number only becomes a signal when it is compared to something — history, peers, or expected range. Agents that quote raw counts feel confident and mislead.

2. **Correlation is not an explanation.** Two trends moving together does not mean one caused the other. Useful agents separate *what we observe* from *why we think it happened* — and label how strong that evidence is.

3. **Facts and judgment must stay separate.** Structured data functions should return indicator flags and reference context, not recommendations. The LLM interprets for the user's situation; if opinions are baked into the data layer, the same tool breaks for every role.

4. **Overconfidence is worse than uncertainty.** Strong agents acknowledge alternative explanations and state evidence tier — especially when reasoning from patterns rather than controlled experiments.

5. **The data-intelligence boundary scales.** One well-designed tool layer can serve many prompts, personas, and workflows. The intelligence layer adapts; the data layer stays auditable.

This workshop uses **open-source project health on GitHub** instead of customer or business data, so you can build and test the same ideas with free public APIs. The architecture is the lesson: contextualized metrics, causal pathways, honest confidence, and guardrails — packaged so you can reuse them in any domain.

---

## Who this is for

No prior Python or terminal experience is required. The [README](../README.md) covers everything you need to get started, including how to use the terminal and run commands.

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

### Quick reference

| Part | File | What you build |
|------|------|----------------|
| Setup | `src/verify.py` | Confirm GitHub + Groq access |
| Part 1 | `src/tools.py` | `get_repo_health` with contextual benchmarks |
| Part 2 | `src/tools.py` | `analyze_causal_patterns` causal reasoning layer |
| Part 3 | `src/agent.py` | Full Groq agent with function calling |
| Part 4 | `.cursor/skills/repo-health-analyst/` | Portable Agent Skill |

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
uv run src/verify.py
```

**Success looks like:**

```
GitHub OK: pallets/flask (xxxxx stars)
Groq OK: ready
```
Both lines must say `OK`.

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
| Historical benchmarks | Whether a deviation matters given relevant context |
| Causal pathway evidence | Which explanation best fits the evidence |
| Methodology notes ("Tier 2 pattern match") | Narrative synthesis |

**Think about it:** Look at the right column. What is the LLM using to make each of those judgments? What happens to the agent's output if the left column is missing, wrong, or incomplete?

**Rule of thumb:** If it could be wrong in a spreadsheet, it belongs in Python. If it requires judgment, it belongs in the LLM — but only if the data layer gives it something to judge and the right context needed to make a sound judgement.

### ADLC planning checklist (for this agent)

Here is what we are building. In a real project, you would figure these out yourself before writing code:

- **Problem:** Help someone evaluate open-source project health on GitHub
- **Inputs:** Repository owner + name (e.g. `pallets/flask`)
- **Outputs:** Structured metrics, causal evidence, narrative briefing
- **Success:** Agent never quotes a metric it did not retrieve; causal claims include evidence tier + alternative

---

### How Parts 1 and 2 work

Each part gives you two ways to implement the code:

- **Option A: Copy the code** — A complete, working code block you paste into `src/tools.py`. This gets you running immediately so you can focus on understanding.
- **Option B: Let Cursor write it** — A plain-English description of the same logic. Highlight it along with the skeleton function in `src/tools.py`, send both to Cursor (`Cmd+L` / `Ctrl+L`), and ask it to implement the function. Compare what Cursor generates to the working code in Option A.

You can do both — paste the code first, then read the description and try Option B to see how Cursor's version compares. This is how you learn to evaluate AI-generated code against a known-good reference.

---

## Build — Part 1: Data tools with context (20 min)

**ADLC phase:** Build — implement the data layer with clear boundaries.

**File:** `src/tools.py`  
**Function:** `get_repo_health(owner, repo)`

### Why this matters

"This repo had 47 commits last month" is useless without context. Your job is to return **numbers plus benchmarks** so the LLM never has to guess.

### Two ways to implement

Pick one:

1. **Option A: Copy the code** — Paste the working code below into `src/tools.py`. This gets you running immediately so you can focus on understanding the logic.
2. **Option B: Let Cursor write it** — Skip to ["What that code does"](#what-that-code-does-in-plain-english), highlight the plain-English description along with the skeleton function in `src/tools.py`, send both to Cursor (`Cmd+L` / `Ctrl+L`), and ask it to implement the function. Compare what it generates to the working code in Option A.

### Option A: The code

Open `src/tools.py` in Cursor. You will see a skeleton with some starter code already in place. Replace the `get_repo_health` function and the `_classify_trend` stub with the code below. Copy and paste the entire block:

```python
def get_repo_health(owner: str, repo: str) -> dict:
    """Retrieve health metrics with historical reference context.

    Returns structured data with indicator flags.
    Does NOT return opinions, recommendations, or severity labels.
    """
    # 1. Fetch the repository
    r = gh.get_repo(f"{owner}/{repo}")
    now = datetime.now(timezone.utc)

    # 2. Get weekly commit counts
    stats = r.get_stats_commit_activity()
    weekly_commits = [week.total for week in stats] if stats else []

    # 3. Compute recent vs. historical activity (z-score)
    recent_4w = weekly_commits[-4:] if len(weekly_commits) >= 4 else weekly_commits
    recent_avg = statistics.mean(recent_4w) if recent_4w else 0

    hist_mean = statistics.mean(weekly_commits) if weekly_commits else 0
    hist_stdev = statistics.stdev(weekly_commits) if len(weekly_commits) >= 2 else 1.0
    z_score = (recent_avg - hist_mean) / hist_stdev if hist_stdev > 0 else 0.0

    # 4. Contributor concentration ("bus factor")
    contributors = list(r.get_stats_contributors() or [])
    if contributors:
        total_commits = sum(c.total for c in contributors)
        top_contributor_share = (
            max(c.total for c in contributors) / total_commits if total_commits else 0
        )
    else:
        total_commits = 0
        top_contributor_share = 0

    # 5. Issue health (last 90 days, excluding pull requests)
    recent_issues = list(r.get_issues(state="all", since=now - timedelta(days=90)))
    open_issues = [i for i in recent_issues if i.state == "open" and i.pull_request is None]
    closed_issues = [i for i in recent_issues if i.state == "closed" and i.pull_request is None]

    # 6. Return a dictionary — facts only, no opinions
    return {
        "repository": f"{owner}/{repo}",
        "stars": r.stargazers_count,
        "forks": r.forks_count,
        "metrics": {
            "commit_activity": {
                "recent_weekly_avg": round(recent_avg, 1),
                "historical_weekly_avg": round(hist_mean, 1),
                "z_score": round(z_score, 2),
                "trend": _classify_trend(weekly_commits),
                "weeks_observed": len(weekly_commits),
            },
            "contributor_concentration": {
                "total_contributors": len(contributors),
                "top_contributor_share": round(top_contributor_share, 2),
            },
            "issue_health": {
                "open_issues_90d": len(open_issues),
                "closed_issues_90d": len(closed_issues),
                "close_ratio": round(
                    len(closed_issues) / max(len(open_issues) + len(closed_issues), 1), 2
                ),
            },
        },
        "indicator_flags": {
            "is_active": recent_avg > 0,
            "is_declining": z_score < -1.0,
            "has_bus_factor_risk": top_contributor_share > 0.50,
            "has_issue_backlog": len(open_issues) > len(closed_issues),
        },
        "retrieved_at": now.isoformat(),
    }


def _classify_trend(weekly: list[int]) -> str:
    """Split weekly commits in half, compare averages, return a trend label."""
    if len(weekly) < 8:
        return "insufficient_data"
    first_half = statistics.mean(weekly[: len(weekly) // 2])
    second_half = statistics.mean(weekly[len(weekly) // 2 :])
    ratio = second_half / first_half if first_half > 0 else 1.0
    if ratio > 1.2:
        return "accelerating"
    if ratio > 0.9:
        return "stable"
    if ratio > 0.6:
        return "slowing"
    return "declining"
```

> **Note:** The first time you call the GitHub stats API for a given repo, it may return empty data while GitHub computes the results. If that happens when you test, wait 5 seconds and try again.

### Option B: What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, highlight the text below along with the skeleton function in `src/tools.py`, press `Cmd+L` (macOS) or `Ctrl+L` (Windows), and ask Cursor to implement it. The skeleton already has the function name, arguments, and docstring — Cursor just needs the logic.

The function should retrieve health metrics for a GitHub repository and return structured data with indicator flags. It should not return opinions, recommendations, or severity labels.

1. **Fetch the repository** using the GitHub client and record the current UTC time.

2. **Get weekly commit counts** from GitHub's commit activity stats. This returns up to 52 weeks of data.

3. **Compute recent vs. historical activity.** Average the last 4 weeks (`recent_avg`), average all weeks (`hist_mean`), and compute a z-score: `(recent_avg - hist_mean) / hist_stdev`. The z-score tells you how unusual recent activity is compared to this repo's own history. A z-score of -1.5 means "noticeably below normal for this project." Use a standard deviation floor of `1.0` if fewer than 2 weeks of data.

4. **Measure contributor concentration ("bus factor").** Get all contributors and calculate `top_contributor_share` — what fraction of total commits came from the single busiest contributor.

5. **Check issue health for the last 90 days.** Fetch all issues, exclude pull requests, count open vs. closed, and compute a `close_ratio`.

6. **Return a dictionary of facts only — no opinions.** The return value includes: `repository`, `stars`, `forks`, nested `metrics` (commit activity, contributor concentration, issue health), boolean `indicator_flags`, and a `retrieved_at` timestamp. The indicator flags are booleans, not subjective labels like "unhealthy" or "concerning":

| Flag | True when... |
|------|------------|
| `is_active` | Recent weekly average > 0 |
| `is_declining` | z-score < -1.0 |
| `has_bus_factor_risk` | Top contributor share > 50% |
| `has_issue_backlog` | More open than closed issues |

**`_classify_trend(weekly)`** classifies the commit trend by splitting the weekly list in half and comparing the averages:

| Condition | Label |
|-----------|-------|
| Fewer than 8 weeks | `insufficient_data` |
| Second half / first half > 1.2 | `accelerating` |
| Ratio > 0.9 | `stable` |
| Ratio > 0.6 | `slowing` |
| Otherwise | `declining` |

### Checkpoint

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

### Two ways to implement

Same choice as Part 1:

1. **Option A: Copy the code** — Paste the working code below into `src/tools.py`.
2. **Option B: Let Cursor write it** — Skip to ["What that code does"](#option-b-what-that-code-does-in-plain-english-1), highlight the description along with the skeleton stubs in `src/tools.py`, and let Cursor implement them.

### Option A: The code

Still in `src/tools.py`, replace the `analyze_causal_patterns` and `_get_alternative` stubs with the code below. Paste it after the `_classify_trend` function you added in Part 1. You also need to add the `CAUSAL_PATHWAYS` data structure — paste it between `_classify_trend` and `analyze_causal_patterns`:

```python
CAUSAL_PATHWAYS = [
    {
        "id": "pathway_001",
        "name": "Maintainer Departure Cascade",
        "mechanism": (
            "When a core maintainer stops contributing, pull request reviews "
            "slow down. Slower reviews discourage external contributors from "
            "submitting PRs. Fewer contributors leads to slower issue resolution "
            "and reduced project visibility."
        ),
        "nodes": ["maintainer_inactive", "review_slowdown", "contributor_decline"],
        "detection": {
            "maintainer_inactive": "Top contributor's last commit > 90 days ago",
            "review_slowdown": "Median days-to-merge increased > 50% vs. 6-month prior",
            "contributor_decline": "Unique contributors this quarter < prior quarter",
        },
        "evidence_tier": 2,
        "confidence_base": 0.55,
    },
    {
        "id": "pathway_002",
        "name": "Release Drought",
        "mechanism": (
            "When a project goes 90+ days without a release, downstream "
            "dependents pin to old versions. Pinned versions reduce new "
            "adoption and increase forks as users patch independently."
        ),
        "nodes": ["no_recent_release", "adoption_stall", "fork_surge"],
        "detection": {
            "no_recent_release": "Last release > 90 days ago",
            "adoption_stall": "Star growth rate declined",
            "fork_surge": "Fork-to-star ratio increasing",
        },
        "evidence_tier": 2,
        "confidence_base": 0.45,
    },
]


def analyze_causal_patterns(owner: str, repo: str) -> dict:
    """Scan repo events for matches against known causal pathways.

    Returns evidence for/against each pathway.
    Does NOT return which pathway "matters most" — that is the LLM's job.
    """
    r = gh.get_repo(f"{owner}/{repo}")
    now = datetime.now(timezone.utc)

    contributors = list(r.get_stats_contributors() or [])
    releases = list(r.get_releases()[:5])

    results = []
    for pathway in CAUSAL_PATHWAYS:
        observations = {}

        if pathway["id"] == "pathway_001":
            if contributors:
                top = max(contributors, key=lambda c: c.total)
                last_week = top.weeks[-1] if top.weeks else None
                if last_week:
                    week_start = datetime.fromtimestamp(last_week.w, tz=timezone.utc)
                    days_since = (now - week_start).days
                    observations["maintainer_inactive"] = {
                        "detected": last_week.c == 0 and days_since > 7,
                        "detail": f"Top contributor: {days_since} days since last active week",
                    }

                recent_contributors = set()
                prior_contributors = set()
                for c in contributors:
                    for w in c.weeks[-13:]:
                        if w.c > 0:
                            recent_contributors.add(
                                c.author.login if c.author else "unknown"
                            )
                    for w in c.weeks[-26:-13]:
                        if w.c > 0:
                            prior_contributors.add(
                                c.author.login if c.author else "unknown"
                            )

                observations["contributor_decline"] = {
                    "detected": len(recent_contributors) < len(prior_contributors),
                    "detail": (
                        f"Recent quarter: {len(recent_contributors)} contributors, "
                        f"prior quarter: {len(prior_contributors)}"
                    ),
                }

        elif pathway["id"] == "pathway_002":
            if releases:
                latest = releases[0]
                days_since_release = (
                    now - latest.created_at.replace(tzinfo=timezone.utc)
                ).days
                observations["no_recent_release"] = {
                    "detected": days_since_release > 90,
                    "detail": (
                        f"Last release: {days_since_release} days ago "
                        f"({latest.tag_name})"
                    ),
                }
            else:
                observations["no_recent_release"] = {
                    "detected": True,
                    "detail": "No releases found",
                }

        nodes_detected = sum(1 for o in observations.values() if o.get("detected"))
        total_nodes = len(observations)

        results.append({
            "pathway": pathway["name"],
            "mechanism": pathway["mechanism"],
            "observations": observations,
            "nodes_detected": nodes_detected,
            "nodes_checked": total_nodes,
            "match_strength": round(nodes_detected / max(total_nodes, 1), 2),
            "evidence_tier": pathway["evidence_tier"],
            "adjusted_confidence": round(
                pathway["confidence_base"] * (nodes_detected / max(total_nodes, 1)), 2
            ),
            "alternative_explanation": _get_alternative(pathway["id"]),
        })

    return {
        "repository": f"{owner}/{repo}",
        "pathways_checked": len(results),
        "results": results,
        "retrieved_at": now.isoformat(),
        "methodology": (
            "Template matching against predefined causal DAGs. "
            "Evidence tier 2 = pattern match (not statistical test). "
            "Confidence is adjusted by the fraction of pathway nodes observed."
        ),
    }


def _get_alternative(pathway_id: str) -> str:
    """Every causal claim must acknowledge at least one alternative."""
    alternatives = {
        "pathway_001": (
            "Seasonal variation: activity commonly drops in summer months "
            "and around holidays. Check contributor timezone distribution."
        ),
        "pathway_002": (
            "Intentional stability: mature projects may reduce release "
            "frequency as the API stabilizes. Check if issue volume also declined."
        ),
    }
    return alternatives.get(pathway_id, "No alternative identified.")
```

### Option B: What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, highlight the text below along with the skeleton stubs in `src/tools.py`, press `Cmd+L` / `Ctrl+L`, and ask Cursor to implement them.

**`CAUSAL_PATHWAYS`** is a list of known cause-effect chains in open-source projects. Each pathway has:

- **Pathway 001 — Maintainer Departure Cascade:** A core maintainer stops contributing, which slows pull request reviews, which discourages external contributors, which leads to slower issue resolution.
- **Pathway 002 — Release Drought:** A project goes 90+ days without a release, which causes downstream dependents to pin old versions, which reduces new adoption and increases forks.

Each pathway includes an `id`, `name`, `mechanism` (the causal chain in plain English), `nodes` (the steps in the chain to check), `detection` rules, an `evidence_tier` of 2 (pattern match, not statistical proof), and a `confidence_base` score.

**`analyze_causal_patterns(owner, repo)`** checks each pathway against real data from the repository:

| Pathway | What it checks |
|---------|---------------|
| 001 | Whether the top contributor's last active week was recent; whether unique contributors this quarter declined compared to last quarter |
| 002 | How many days since the last release |

For each pathway, it builds a result with: per-node `observations` (detected or not, with detail strings), counts of `nodes_detected` vs. `nodes_checked`, a `match_strength` ratio, the `evidence_tier`, an `adjusted_confidence` (base confidence scaled by match strength), and an `alternative_explanation`.

The function returns evidence, not conclusions. It does **not** pick a "winner" pathway — that is the LLM's job.

**`_get_alternative(pathway_id)`** returns a competing explanation for each pathway. Every causal claim must acknowledge at least one alternative:

- Pathway 001: seasonal slowdown (holidays, summer)
- Pathway 002: intentional stability in a mature project

### Evidence tiers (use these in Part 3)

| Tier | Strength | How to phrase it |
|------|----------|------------------|
| 1 | Temporal sequence | "Following X, we observed Y..." |
| 2 | Pattern match | "This matches a known pattern..." |
| 3 | Peer comparison | "Similar projects without X didn't show Y..." |
| 4 | Statistical test | "Across N projects, X predicts Y (p < 0.05)..." |

Your tools are **Tier 2**. The LLM must say so.

### Checkpoint

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

### Two ways to implement

Same choice as Parts 1 and 2:

1. **Option A: Copy the code** — Paste the full working file below.
2. **Option B: Let Cursor write it** — Skip to ["What that code does"](#option-b-what-that-code-does-in-plain-english-2), create an empty file, and let Cursor build it from the description.

### Option A: The code

Create a new file: in Cursor's file explorer, right-click the `src/` folder, choose **New File**, and name it `agent.py`. Paste the entire block below:

```python
import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq

from config import get_groq_model
from tools import get_repo_health, analyze_causal_patterns

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = get_groq_model()

# Tool schemas — the LLM's menu of available functions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_repo_health",
            "description": (
                "Get health metrics for a GitHub repository with historical "
                "reference distributions. Returns indicator flags (is_declining, "
                "has_bus_factor_risk, etc.) and z-scores against the repo's own "
                "history. Does NOT return opinions or recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "GitHub org or user (e.g. 'pallets')",
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name (e.g. 'flask')",
                    },
                },
                "required": ["owner", "repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_causal_patterns",
            "description": (
                "Scan a GitHub repository's event timeline for matches against "
                "known causal pathway templates (e.g. maintainer departure cascade, "
                "release drought). Returns evidence for/against each pathway with "
                "confidence scores and alternative explanations. Evidence is at "
                "Tier 2 (pattern matching). Does NOT return conclusions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {
                        "type": "string",
                        "description": "GitHub org or user",
                    },
                    "repo": {
                        "type": "string",
                        "description": "Repository name",
                    },
                },
                "required": ["owner", "repo"],
            },
        },
    },
]

# Map tool names to Python functions
TOOL_FUNCTIONS = {
    "get_repo_health": get_repo_health,
    "analyze_causal_patterns": analyze_causal_patterns,
}

# System prompt — your agent's rules (write your own!)
# Think about what you learned in Parts 1 and 2:
#   - When should the agent call each tool?
#   - How should it present numbers from the data layer?
#   - How should it handle causal claims and uncertainty?
#   - What should it never do?
SYSTEM_PROMPT = """\
TODO: Write your system prompt here. Describe the agent's role and rules.
"""


# Agent loop — LLM decides which tools to call, Python runs them, LLM synthesizes
def run_agent(user_message: str) -> str:
    """Run the full agent loop: user -> LLM -> tools -> LLM -> response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                print(f"  [Calling {fn_name}({fn_args})]")

                result = TOOL_FUNCTIONS[fn_name](**fn_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })
        else:
            return msg.content


# Naive agent — no tools, no rules, for comparison
def run_naive_agent(user_message: str) -> str:
    """A naive agent with no tools and no reasoning rules — for comparison."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) or "Analyze the health of the pallets/flask repository."

    print("=" * 60)
    print("CAUSAL AGENT")
    print("=" * 60)
    print(run_agent(query))

    print("\n" + "=" * 60)
    print("NAIVE AGENT (no tools, no rules)")
    print("=" * 60)
    print(run_naive_agent(query))
```

### Option B: What that code does (in plain English)

Create a new file: in Cursor's file explorer, right-click the `src/` folder, choose **New File**, and name it `agent.py`. Then highlight the description below, press `Cmd+L` / `Ctrl+L`, and ask Cursor to build the file.

**Imports and setup.** Import `json`, `os`, `sys`, `dotenv`, `Groq`, `get_groq_model` from `config.py`, and the two tool functions from `tools.py`. Load `.env`, create the Groq client, and set `MODEL = get_groq_model()`. The default model is `openai/gpt-oss-20b`; set `GROQ_MODEL=qwen/qwen3.6-27b` in `.env` to use Qwen instead.

**Tool schemas (`TOOLS`).** Define two function schemas in Groq's function-calling format. Each has a `name` (matching the Python function), a `description` that says what the tool returns *and* what it does not return, and `parameters` for `owner` and `repo` (both required strings). The descriptions are guardrails — saying "Does NOT return opinions" keeps the data-intelligence boundary intact.

**Tool function map (`TOOL_FUNCTIONS`).** A dictionary mapping tool name strings to the actual Python functions.

**System prompt (`SYSTEM_PROMPT`).** This is the part where you decide how the agent should behave. Think about what you learned in Parts 1 and 2: the data layer returns facts with context, evidence tiers, and alternative explanations. The system prompt should tell the LLM how to use all of that responsibly. Consider: When should the agent call each tool? How should it present numbers? How should it handle uncertainty? What should it never do?

**Agent loop (`run_agent`).** Takes a user message, puts it in a messages list with the system prompt, and loops: send messages to Groq with `tools=TOOLS`, if the model requests tool calls then run each Python function and append the results to messages, otherwise return the text response. Use `model=MODEL`. Print each tool call so you can see what happened.

**Naive agent (`run_naive_agent`).** Same model, but with a generic system prompt ("You are a helpful assistant") and no tools. This exists for comparison — to show the difference between an agent with structured data and one without.

**Main block.** When run from the command line, take an optional query argument (default: "Analyze the health of the pallets/flask repository"), run both agents on the same query, and print their outputs side by side.

### Checkpoint ✓

```bash
uv run src/agent.py
```

**Success:**

- Terminal shows `[Calling get_repo_health(...)]`
- Causal agent output cites real metrics with context
- Naive agent invents or guesses numbers — **that is the point**

### Try other repos

```bash
uv run src/agent.py "Analyze the health of facebook/react"
uv run src/agent.py "Should I contribute to psf/requests?"
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

Start the file with YAML frontmatter — a block of metadata between `---` lines at the very top. Cursor reads this to know when to activate the skill and what it needs to run:

```yaml
---
name: repo-health-analyst
description: >
  Analyze GitHub repository health using causal reasoning. Use when asked to
  evaluate project health, maintenance, contributor risk, or adoption decisions.
compatibility: Requires Python 3.11+, uv, GITHUB_TOKEN, GROQ_API_KEY.
---
```

- **`name`** identifies the skill in Cursor's skill list.
- **`description`** tells Cursor when to suggest this skill — it matches against what you type in chat. If you ask "evaluate the health of this repo," Cursor sees the keywords and knows this skill is relevant.
- **`compatibility`** lists what must be installed for the skill to work.

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
uv run src/agent.py
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

### Project structure

After setup, the repo looks like this. Files you create during the workshop are marked with **← you create**.

```
causal-agent-workshop/
├── .venv/                             # ← created by uv sync (virtual environment)
├── docs/
│   └── workshop-guide.md              # This guide (ADLC-aligned)
├── solutions/                         # Instructor reference (optional)
│   ├── skills/
│   │   └── repo-health-analyst/
│   │       ├── scripts/
│   │       │   └── tools.py
│   │       └── SKILL.md
│   ├── README.md
│   ├── agent.py
│   ├── config.py
│   ├── tools.py
│   └── verify.py
├── src/
│   ├── agent.py                       # ← you create in Part 3
│   ├── config.py                      # Groq model selection (GROQ_MODEL)
│   ├── list_models.py                 # Lists available Groq models
│   ├── tools.py                       # Parts 1 + 2 (you implement these)
│   └── verify.py                      # Setup verification
├── .cursor/skills/                    # ← you create in Part 4
│   └── repo-health-analyst/
│       ├── scripts/
│       │   └── tools.py
│       └── SKILL.md
├── .env                               # ← you create in setup (from .env.sample)
├── .env.sample                        # Template for API keys
├── .gitignore
├── .python-version
├── README.md                          # Setup instructions
├── pyproject.toml
└── uv.lock
```

### Commands

Open the terminal in Cursor from the **project root**, then run these **one at a time**:

```bash
# Verify setup
uv run src/verify.py

# After completing Parts 1–2 — test health metrics
uv run --directory src python -c "from tools import get_repo_health; import json; print(json.dumps(get_repo_health('pallets','flask'), indent=2, default=str))"

# After completing Part 3 — run the causal agent
uv run src/agent.py
uv run src/agent.py "Analyze the health of facebook/react"

# After completing Part 4 — run skill scripts
uv run python .cursor/skills/repo-health-analyst/scripts/tools.py health pallets flask
uv run python .cursor/skills/repo-health-analyst/scripts/tools.py causal pallets flask
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
