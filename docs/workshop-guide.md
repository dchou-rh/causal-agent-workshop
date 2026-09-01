# Workshop Guide

**Build an Intelligence Agent, Not a Chatbot**

> *Not what happened. Why it happened. What happens next.*

A 75-minute hands-on workshop on building agents that reason about data — not just repeat it.

## Start here — setup check (5 min)

**Not an ADLC phase** — environment verification before **Plan**. If you already completed the [pre-workshop setup](../README.md), run through this **at the start of the workshop** so you have the latest files and a working environment.

### 1. Sync the latest files

If you cloned this repo during pre-workshop setup, your local copy may be out of date. Pull the latest guide, stubs, and exercises **before you read further**.

Open a terminal in Cursor (**View → Terminal**). Go to the **project root** — the folder that contains `src/` and `docs/` (often named `causal-agent-workshop`):

```bash
cd causal-agent-workshop   # skip if you are already in the project root
git pull
```

You should see files update, or `Already up to date.`

**First time today?** Clone the repo instead (see [README — Clone this repository](../README.md#step-4-clone-this-repository)):

```bash
git clone https://github.com/dchou-rh/causal-agent-workshop.git
cd causal-agent-workshop
```

**`git pull` failed?** Fetch and reset your branch to match the remote (this **discards uncommitted changes** in this repo):

```bash
git fetch origin
git reset --hard origin/main
```

If you already edited files in `src/` or `.cursor/skills/` and want to keep that work, copy those files elsewhere first, reset, then copy them back.

### 2. Run the setup check

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

## Why causal reasoning?

Many agent demos emphasize retrieval: pull a metric, summarize it, call it intelligence. In practice, that often leaves users with the same question they started with — *so what?*

Effective decision-support agents are built around a simple idea: users need three things — not one:

| Question | What users actually need |
|----------|--------------------------|
| **What happened?** | Accurate data |
| **Why did it happen?** | Causal context — plausible mechanisms, not just correlated trends |
| **What happens next?** | Grounded judgment a human can act on |

That framing — *not what happened, but why it happened and what happens next* — is why this workshop goes beyond wiring an LLM to an API.

### Pearl's ladder — why "why" is not one question

Computer scientist **Judea Pearl** ([*The Book of Why*](https://yalebooks.yale.edu/book/9780465097609/the-book-of-why/)) formalized a core problem in analytics: models can **predict** well yet **explain** poorly. Causal questions live on a **ladder of causation** with three rungs, each requiring strictly stronger assumptions and data:

| Rung | Question type | Formal move | What it requires | Example |
|------|---------------|-------------|------------------|---------|
| **1. Association** | What co-occurs in the data? | See P(Y given X) | Observational data only — correlation, trends, co-movement | "Ice cream sales and drowning deaths both rise in summer" |
| **2. Intervention** | What if we *do* X? | Estimate P(Y given do(X)) | Randomized experiment, natural experiment, or **identified** estimand from observational data (backdoor adjustment, instrumental variables, etc.) | "If we run the ad campaign, will sales go up?" |
| **3. Counterfactual** | What if X had been different, *given what we observed*? | Compare worlds under a structural model | **Structural causal model** (SCM) or equivalent — a DAG of mechanisms — to ask about worlds that did not happen | "Would this patient have recovered if they had taken the drug?" |

Pearl's ladder makes a sharp distinction: association is not causation. **Many analytics workflows — and many LLM answers — stay on rung 1.** They narrate co-occurrence as if it were mechanism. Sound causal practice asks *identification* questions ("what must be true for this estimand to be causal?") before *estimation* questions ("what is the effect size?"). Default agents often skip both unless you **engineer** the data and reasoning layers.

This workshop does not implement `do`-calculus or fit SCMs. It teaches you to **place claims on the ladder honestly** — and to build tools that return evidence at a known tier instead of letting the LLM imply rung 3 from rung 1 data.

### What this workshop adds to Pearl's ladder

Pearl's rungs classify the **type** of question. In [Part 2](#part-2--build-causal-reasoning-17-min) you will add a practical **evidence tier** rubric (Tiers 1–4) for how strongly an agent *could* justify a claim. **This workshop implements Tiers 1–2 in code**; Tiers 3–4 are described for completeness but are not produced by `tools.py` unless you extend it. Tiers 1–2 remain on the **association rung**; Tiers 3–4 would add peer comparison and population-level tests — still not intervention or counterfactual proof without experiments.

| Design choice | Causal-inference analogue | What you build |
|---------------|---------------------------|----------------|
| Contextualized metrics (Part 1) | Historical baselines add context (not confounding adjustment) | z-scores vs self-history, not raw counts |
| Pathway templates (Part 2) | Mechanism hypotheses (DAG-style stories, not formal graphs) | `CAUSAL_PATHWAYS` as domain templates |
| `alternative_explanation` | Reporting competing explanations | Every pathway returns a rival story |
| Evidence tiers in the prompt | Epistemic humility about identification | Prompt should require tier labels, not proof |
| Naive agent (Part 3) | Unidentified causal narration | Confident prose with no instruments |

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

Neither replaces the other. Production systems often use **both**: ML for scoring at scale, agents for interpretation, investigation, and communication. The mistake is treating a general-purpose LLM chatbot as a substitute for either — it has no **domain-specific fitted model** for your data and no structured evidence layer unless you build one.

This workshop focuses on that missing layer: **tools that return auditable facts**, plus **reasoning rules** that force the agent to contextualize metrics, separate correlation from mechanism, and admit uncertainty.

### Design patterns for intelligence agents (not chatbots)

These patterns show up when an agent must support real decisions. They are design choices, not laws — illustrated here and in Red Hat's [enterprise data agent](https://www.redhat.com/en/blog/we-built-enterprise-data-agent-and-you-can-too) write-up:

1. **Metrics without baselines are noise.** A number only becomes a signal when it is compared to something — history, peers, or expected range. Agents that quote raw counts feel confident and mislead.

2. **Correlation is not an explanation.** Two trends moving together does not mean one caused the other. Useful agents separate *what we observe* from *why we think it happened* — and label how strong that evidence is.

3. **Facts and judgment should stay separate.** Structured data functions should return indicator flags and reference context, not recommendations. The LLM interprets for the user's situation; if opinions are baked into the data layer, the same tool breaks for every role.

4. **Overconfidence is worse than uncertainty.** Strong agents acknowledge alternative explanations and state evidence tier — especially when reasoning from patterns rather than controlled experiments.

5. **The data-intelligence boundary scales.** One well-designed tool layer can serve many prompts, personas, and workflows. The intelligence layer adapts; the data layer stays auditable.

That blog post argues agents fail when they guess without sources, when business context is missing, and when data and judgment are mixed. Production teams address that with a **data foundation** (one source of truth per domain), a **guidance architecture** (routing rules and documentation the LLM consults before answering), a **staged pipeline** (retrieve → narrow → reason → return, with each step logged), and **skills-based packaging** (capabilities and rules as modular documents the agent loads on demand). Trust, accountability, and inherited access control matter as much as model choice.

This workshop uses **open-source project health on GitHub** instead of customer or business data, so you can build and test the same ideas with free public APIs. The architecture is the lesson: contextualized metrics, causal pathways, honest confidence, and guardrails — packaged so you can reuse them in other domains.

---

## Who this is for

Designed for **graduate students and researchers** building or evaluating AI agents — especially those with exposure to statistics, causal inference, or ML who want a hands-on bridge from **identification and evidence** to **agent architecture**.

No prior Python or terminal experience is required. The [README](../README.md) covers everything you need to get started, including how to use the terminal and run commands. Familiarity with Pearl's ladder, DAGs, or observational causal methods will deepen the discussion; the workshop is self-contained if you are new to agents.

**Before you begin:** Complete setup in the [README](../README.md). You need Cursor, API keys, and a successful run of `verify.py`. At the workshop start, run the [setup check](#start-here--setup-check-5-min) (sync files + verify).

---

## What you will have at the end

A small agent that:

1. **Pulls real data** from GitHub (not guesses)
2. **Adds context** to every metric (benchmarks, trends, flags)
3. **Reasons causally** with evidence tiers and alternative explanations (when the model follows the rules)
4. **Packages as a portable Agent Skill** for Cursor and other tools

---

## Schedule at a glance

| Time | ADLC phase | What you do |
|------|------------|-------------|
| 0:00–0:05 | *(Pre-workshop)* | [Setup check](#start-here--setup-check-5-min) — sync files + `verify.py` |
| 0:05–0:13 | **Plan** | Data-intelligence boundary + Cursor Plan mode |
| 0:13–0:30 | **Build** | Part 1 — `get_repo_health` |
| 0:30–0:47 | **Build** | Part 2 — `analyze_causal_patterns` |
| 0:47–1:00 | **Test** | Part 3 — wire tools to Groq; smoke-test the agent |
| 1:00–1:08 | **Deploy** | Part 4 — package as an Agent Skill |
| 1:08–1:15 | **Evaluate** | Compare causal vs naive agent + production architecture close-out |

**Running behind?** Focus on Part 3 — that is where the agent comes alive. Parts 1–2 are the foundation; Part 4 is packaging what you already built. Skip Part 4 step 5 (in-chat skill demo) or the optional [Operate & monitor appendix](#optional-operate--monitor-discussion-8-min) if you are short on time.

### Quick reference

| ADLC phase | Part | File | What you build |
|------------|------|------|----------------|
| *(Pre-workshop)* | Setup | `src/verify.py` | Confirm GitHub + Groq access |
| **Plan** | — | — | Problem scope, data-intelligence boundary, Cursor plan |
| **Build** | 1 | `src/tools.py` | `get_repo_health` with contextual benchmarks |
| **Build** | 2 | `src/tools.py` | `analyze_causal_patterns` causal reasoning layer |
| **Test** | 3 | `src/agent.py` | Full Groq agent with function calling |
| **Deploy** | 4 | `.cursor/skills/repo-health-analyst/` | Portable Agent Skill |
| **Evaluate** | — | — | Causal vs naive comparison + production close-out |
| **Operate & monitor** *(optional)* | — | — | Ongoing discipline after launch — see appendix |

---

## ADLC: How this workshop is structured

**ADLC** (Agent Development Lifecycle) is [IBM's framework](https://www.ibm.com/think/topics/agent-development-lifecycle-adlc) for building and operating AI agents in real workflows — one useful lifecycle model, not an industry-wide standard like SDLC. It maps agent work onto iterative phases:

**plan → build → test → deploy → operate → monitor**

Traditional software (**SDLC**) is deterministic: the same input yields the same output, and failures usually crash or throw obvious errors. Agents are probabilistic: the same prompt can yield different answers, and failures often look plausible — a confident wrong answer is harder to spot than a stack trace. ADLC addresses that shift through behavioral evaluation, guardrails, and ongoing monitoring rather than ship-once-and-forget.

### How the workshop maps to ADLC

This workshop covers **plan through deploy** in 75 minutes, plus **evaluate** as the wrap-up. **Operate & monitor** is optional reading after the session.

| IBM ADLC phase | Workshop section | What you produce |
|----------------|------------------|------------------|
| **Plan** | Plan: The data-intelligence boundary | Problem scope, success criteria, Cursor plan |
| **Build** | Part 1 + Part 2 | `tools.py` — facts, flags, causal evidence |
| **Test** | Part 3 | `agent.py` — agent loop wired and smoke-tested |
| **Deploy** | Part 4 | Agent Skill (`SKILL.md` + scripts) |
| **Evaluate** | Compare: Causal vs naive agent | Behavioral comparison + production architecture *(workshop label — not an IBM phase name)* |
| **Operate & monitor** | Optional appendix (end of guide) | Drift, accountability, compliance — after launch |

**Pre-workshop setup** ([Start here — setup check](#start-here--setup-check-5-min)) is environment verification only — not an ADLC phase.

**Why Evaluate comes after Deploy on the schedule:** Part 3 smoke-tests the agent during **Test**. The **Evaluate** section at the end is the deliberate payoff — side-by-side comparison after you have packaged the skill — so you leave with a clear picture of why tools + rules matter.

**The four numbered parts** align to ADLC as: **Build** (Parts 1–2), **Test** (Part 3), **Deploy** (Part 4). Plan and Evaluate are separate sections that bookend the hands-on build.

In 75 minutes we also touch five ADLC habits you can use on any agent project:

| ADLC habit | What it means here |
|------------|-------------------|
| **Plan before you prompt** | Align on the problem, success criteria, and data sources — use Cursor Plan mode |
| **Separate data from judgment** | Python returns facts; the LLM interprets them (tools + orchestration, not prompt-only) |
| **Build guardrails in** | System prompts, tool boundaries, evidence tiers — designed in up front, not bolted on after demos break |
| **Evaluate, don't just demo** | Compare causal vs naive agents; production teams add benchmarks and regression tests |
| **Package for reuse** | Ship tools + rules as an Agent Skill — a first step toward deploying into everyday workflows |

Each section below calls out which ADLC phase you are in and what deliverable you are producing.

---

## Plan: The data-intelligence boundary (8 min)

**ADLC phase: Plan** — define the problem, scope, and success criteria. Practice **Plan mode** in Cursor before any code.

*Light coding-free discussion, then a short Plan-mode exercise (~4 min).*

### The core question

Most "AI agent" tutorials connect an LLM to an API and stop. That produces a **chatbot** — it talks confidently but may invent numbers.

This workshop builds an **intelligence agent** — one designed to **tie claims to retrieved data** and state how confident each claim should be. That is the target; you still need prompts, tools, and evaluation to get there reliably.

You will build the workshop version of that enterprise split: `tools.py` for auditable facts (your data layer), prompts and `SKILL.md` for how to interpret them (your guidance architecture).

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
- **Success (target behavior):** Agent should not quote a metric unless a tool returned it; causal claims should include evidence tier + alternative (verify in the [Evaluate](#compare-causal-vs-naive-agent-7-min) section)

---

### Try it: Plan in Cursor (~4 min)

**ADLC in practice:** The checklist above is your plan. In Cursor, [**Plan mode**](https://cursor.com/docs/agent/plan-mode) supports the same *idea* — research the codebase, ask clarifying questions, and produce a **reviewable plan** you can edit before any code runs. That is *plan before you prompt* in action.

#### Steps

1. Open Cursor chat (**`Cmd+L`** / **`Ctrl+L`**).
2. Press **`Shift+Tab`** from the chat input (or use the **mode picker**) until the mode shows **Plan**.
3. Copy the prompt below, paste it into chat, and press **Enter**.
4. Answer any clarifying questions Cursor asks (pick sensible defaults if you are unsure).
5. When the plan appears, read it — especially which work belongs in `tools.py` vs. the LLM.

**Do not click Build yet.** The learning goal is to **review the plan** against the data-intelligence boundary. Build switches to Agent mode and starts editing files — save that for [Option B](#option-b-let-cursor-write-it) in Parts 1–3 if you want.

> **Workshop quota:** Plan mode uses one Agent session. In a live session, the facilitator can demo on one screen while the room discusses the plan. Pairs work too: one partner runs Plan mode, the other scores the plan against the table above.

#### Copy-paste prompt

```
Plan how to implement this workshop's GitHub repo health agent (causal-agent-workshop).

Before any code, produce a structured implementation plan that covers:

1. Problem, inputs, outputs, and success criteria (measurable — e.g. no hallucinated metrics)
2. Data layer (src/tools.py): what each tool returns — facts, flags, z-scores, evidence tiers only; explicitly what must NOT be returned (opinions, recommendations, severity labels)
3. Intelligence layer: system prompt rules, evidence tiers, when to call which tool
4. Files and order of work (Parts 1–4: tools → agent.py → Agent Skill)
5. Risks and guardrails (overconfidence, correlation vs causation, token/API limits)

Read the existing stubs in src/tools.py and the workshop structure in docs/workshop-guide.md for context.

Planning only — do not implement or edit files yet.
```

#### Review the plan (2 min)

With the plan open, check as a group (or with your partner):

1. Does the plan keep **facts in Python** and **judgment in the LLM** — matching the table above?
2. Are success criteria **testable** (not vague like "good answers")?
3. What would you change before clicking **Build**?

Optional: click **Save to workspace** on the plan file so you can reference it during Parts 1–4.

#### Connect to the rest of the workshop

| Path | What you do |
|------|-------------|
| **Default (Option A)** | Copy the working code from this guide in Parts 1–3 — compare your mental model to the plan you just reviewed |
| **Option B** | Return to your plan in Parts 1–3 and click **Build** on the relevant steps, or start a fresh Plan for each part — then diff Cursor's output against Option A |

Either way, the plan is the contract. The code is the implementation.

---

### Live workshop tip (Cursor free tier)

This workshop does **not** require Cursor AI for Parts 1–3. For live sessions, **default to Option A** (copy the code) so everyone finishes on time without burning limited Agent requests. The **Plan** section above uses one Plan session (review only — no Build). **Part 4** includes an optional in-chat skill demo (step 5) — reserve one Agent request for that, or skip it and verify your skill with the terminal commands in step 4. If you want to try Option B in Parts 1–3, **pair up**: one partner implements Option A while the other uses Cursor Plan then Build, or swap roles between parts.

### How Parts 1–3 work

Each part gives you two ways to implement the code:

- **Option A: Copy the code** — A complete, working code block you paste into `src/tools.py`. This gets you running immediately so you can focus on understanding.
- **Option B: Let Cursor write it** — Copy the ready-made prompt for that part into Cursor chat (`Cmd+L` / `Ctrl+L`). Cursor will edit the file for you. Compare what it generates to the working code in Option A.

You can do both — paste the code first, then read the description and try Option B to see how Cursor's version compares. This is how you learn to evaluate AI-generated code against a known-good reference.

---

## Part 1 · Build: Data tools with context (17 min)

**ADLC phase: Build** — implement the data layer with clear boundaries.

**File:** `src/tools.py`  
**Function:** `get_repo_health(owner, repo)`

### Why this matters

"This repo had 47 commits last month" is weak without context. Your job is to return **numbers plus benchmarks** so the LLM is less tempted to invent context on its own.

### Two ways to implement

Pick one:

1. **Option A: Copy the code** — Paste the working code below into `src/tools.py`. This gets you running immediately so you can focus on understanding the logic.
2. **Option B: Let Cursor write it** — Skip to [Option B](#option-b-let-cursor-write-it) and copy the prompt into Cursor chat.

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

### Option B: Let Cursor write it

1. Open `src/tools.py` in Cursor (the skeleton with `NotImplementedError` stubs is already there).
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows) to open chat.
3. Copy the entire prompt below and paste it into chat. Press Enter.
4. Review the changes before accepting — make sure it only edits `get_repo_health` and `_classify_trend`.

**Cursor prompt (copy and paste):**

```
Implement get_repo_health and _classify_trend in src/tools.py for this workshop project.

The file already has imports, load_dotenv(), and gh = Github(os.environ["GITHUB_TOKEN"]). Replace the NotImplementedError stubs only — do not rewrite the whole file.

get_repo_health(owner, repo) must return structured facts only (no opinions, recommendations, or severity labels):

1. Fetch the repo and record the current UTC time.
2. Get weekly commit counts from GitHub commit activity stats (up to 52 weeks).
3. Compute recent_avg (mean of last 4 weeks), hist_mean, hist_stdev (use 1.0 if fewer than 2 weeks), and z_score = (recent_avg - hist_mean) / hist_stdev.
4. From contributor stats, compute top_contributor_share (bus factor).
5. From issues in the last 90 days (exclude pull requests), count open vs closed and compute close_ratio.
6. Return a dict with: repository, stars, forks, metrics (commit_activity, contributor_concentration, issue_health), indicator_flags, and retrieved_at (ISO timestamp).

Indicator flags (booleans only):
- is_active: recent weekly average > 0
- is_declining: z-score < -1.0
- has_bus_factor_risk: top contributor share > 0.50
- has_issue_backlog: more open than closed issues

_classify_trend(weekly) must return one of: insufficient_data (< 8 weeks), accelerating (second-half/first-half > 1.2), stable (> 0.9), slowing (> 0.6), otherwise declining.

Match the existing code style. Do not add new dependencies.
```

### What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, use the prompt above, then read this section to verify Cursor's output matches the intent.

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

You just defined the **contract** for your data layer. Every consumer of `get_repo_health` — different prompts, different users — gets the same facts. That is how you build agents that scale beyond a single demo. In production, teams call this **data product ownership**: one source of truth, maintained by people who know the domain.

---

## Part 2 · Build: Causal reasoning (17 min)

**ADLC phase: Build** — add structured evidence the LLM can reason over.

**File:** `src/tools.py` (same file)  
**Functions:** `analyze_causal_patterns`, `_get_alternative`

### Why correlation is not enough

Part 1 tells you *what* is happening. Causal reasoning asks *why* — and requires honesty about **which rung of Pearl's ladder** your evidence supports.

In observational settings (GitHub timelines, issue trackers, contributor stats), you almost always have **association** data. Confounding is routine: a repo's commit drop might track a maintainer's absence, a holiday quarter, a platform outage, or a shift in project scope. Without a design or model that addresses confounding, a compelling narrative is still **unidentified** — the same statistical pattern fits multiple DAGs.

Agents make this worse by default: LLMs are fluent at **post hoc stories**. Your job in Part 2 is to constrain that fluency with **structured hypotheses** (pathways), **competing explanations**, and **explicit tiers** — so the model reasons *over* evidence instead of inventing mechanism.

### Pearl's ladder — three kinds of causal questions (review)

You saw Pearl's three rungs in [Why causal reasoning?](#pearls-ladder--why-why-is-not-one-question). Here is how they map to this lab:

| Rung | Question type | Example | What it requires | Can this workshop's agent answer it? |
|------|---------------|---------|------------------|--------------------------------------|
| **1. Association** | What do we observe together? | "Smokers have higher lung cancer rates" | Observational data only | **Yes** — Parts 1–2 report co-occurring metrics and patterns |
| **2. Intervention** | What if we *act*? | "Does a smoking-cessation program reduce risk?" | Experiment, quasi-experiment, or identified estimand (Pearl's **do** operator) | **No** — needs design beyond GitHub logs |
| **3. Counterfactual** | What if things had been different — *why* did this happen? | "Would she have gotten sick if she had never smoked?" | SCM or DAG of mechanisms + untestable assumptions | **No** — needs structural model, not correlation |

The same lesson applies here: many analytics workflows — and many LLM answers — stay on rung 1. They describe co-occurrence and present it as explanation. **Pattern matching on a pathway template is still rung 1** unless you have validated the mechanism and identification strategy behind the template.

**For seminar discussion:** Your `CAUSAL_PATHWAYS` entries are **hypothesized mechanisms** — subgraphs of a larger DAG. Which edges would you need to condition on (backdoor paths) to interpret a pathway match as supportive of X → Y? What would an **instrument** look like in open-source health (if anything)?

### Evidence tiers — how strong is the claim?

Pearl's ladder classifies the *type* of question. This workshop adds a practical rubric for *how much* an agent can justify from **observational GitHub data**:

| Tier | Strength | What it takes | How to phrase it |
|------|----------|---------------|------------------|
| 1 | Temporal sequence | A before B in the data | "Following X, we observed Y..." |
| 2 | Pattern match | Multiple signals fit a known causal pathway template | "This matches a known pattern..." |
| 3 | Peer comparison | Similar cases without X don't show Y | "Peer projects without X didn't show Y..." |
| 4 | Statistical test | Tested across many cases | "Across N projects, X predicts Y (p < 0.05)..." |

> **Workshop scope:** `analyze_causal_patterns` returns **Tier 2** evidence only. Tiers 3–4 are part of the rubric for honest narration — do not let the LLM claim Tier 3 or 4 unless you build tools that produce peer comparisons or statistical tests.

**Tiers 1–2 stay on Pearl's association rung** — observational evidence only. Tiers 3–4 would add comparative or population-level rigor (closer to **external validity** and **statistical confirmation**, still not `do(X)`). Interventions and true counterfactuals need experiments, instruments, or SCMs this workshop does not build — but your agent should **not pretend** it has them.

| If the agent says… | Implied rung | Honest? |
|--------------------|--------------|---------|
| "Following maintainer inactivity, we observed declining commits" | 1 (association) | Yes, at Tier 1 |
| "This matches a maintainer-departure cascade pattern" | 1 (structured association) | Yes, at Tier 2 |
| "Adding a maintainer would restore velocity" | 2 (intervention) | **No** — not identified from GitHub logs alone |
| "The decline would not have happened without burnout" | 3 (counterfactual) | **No** — needs SCM + untestable assumptions |

### What "pattern matching" means here

In Part 2 you define **causal pathways** — plain-English stories of how maintainer attrition or release gaps might lead to decline. Think of each pathway as a **mechanism template** (a story you could draw as a DAG, but this workshop does not formalize one). `analyze_causal_patterns` does not *prove* those stories. It **pattern-matches**: it checks whether real repo data lines up with a **subset of nodes** you can proxy from GitHub (e.g. top contributor inactive *and* contributor count fell).

That is **Tier 2** evidence — structured association on rung 1, not proof. The pathway may be a plausible explanation, or a seasonal slowdown could fit the same signals. That is why every pathway returns an `alternative_explanation` and the system prompt should require reporting the tier honestly — the agent is doing **abductive** reasoning (best story fit), not **causal identification**.

**This workshop operates at pattern matching (Tier 2).** The goal is responsible *why* reasoning under real constraints: explicit mechanisms, alternatives, and ladder placement — not causal certainty or policy prescriptions from observational GitHub data alone.

**Extension (post-workshop):** To climb Pearl's rungs in production, you would add interventional data (A/B tests on maintainer programs), quasi-experiments (repos that gained/lost maintainers exogenously), or formal SCMs with sensitivity analysis. The architecture you build today — facts in tools, tiers in prompts — scales to those richer sources without changing the data-intelligence boundary.

### Two ways to implement

Same choice as Part 1:

1. **Option A: Copy the code** — Paste the working code below into `src/tools.py`.
2. **Option B: Let Cursor write it** — Skip to [Option B](#option-b-let-cursor-write-it-1) and copy the prompt into Cursor chat.

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
        "nodes": ["maintainer_inactive", "contributor_decline"],
        "detection": {
            "maintainer_inactive": "Top contributor's last commit > 90 days ago",
            "contributor_decline": "Unique contributors this quarter < prior quarter",
        },
        "evidence_tier": 2,
        "confidence_base": 0.55,  # workshop weight — not empirically calibrated
    },
    {
        "id": "pathway_002",
        "name": "Release Drought",
        "mechanism": (
            "When a project goes 90+ days without a release, downstream "
            "dependents pin to old versions. Pinned versions reduce new "
            "adoption and increase forks as users patch independently."
        ),
        "nodes": ["no_recent_release"],
        "detection": {
            "no_recent_release": "Last release > 90 days ago",
        },
        "evidence_tier": 2,
        "confidence_base": 0.45,  # workshop weight — not empirically calibrated
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
                    week_start = last_week.w
                    if not isinstance(week_start, datetime):
                        week_start = datetime.fromtimestamp(week_start, tz=timezone.utc)
                    elif week_start.tzinfo is None:
                        week_start = week_start.replace(tzinfo=timezone.utc)
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
            "Template matching against predefined pathway hypotheses. "
            "Evidence tier 2 = pattern match (not statistical test). "
            "adjusted_confidence = confidence_base × match_strength; "
            "confidence_base is a workshop weight, not a calibrated probability."
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

### Option B: Let Cursor write it

1. Open `src/tools.py` in Cursor (your Part 1 functions should already be in place).
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows) to open chat.
3. Copy the entire prompt below and paste it into chat. Press Enter.
4. Review the changes before accepting — make sure it adds `CAUSAL_PATHWAYS` and implements `analyze_causal_patterns` and `_get_alternative`.

**Cursor prompt (copy and paste):**

```
Implement Part 2 in src/tools.py: CAUSAL_PATHWAYS, analyze_causal_patterns, and _get_alternative.

Replace the NotImplementedError stubs. Add CAUSAL_PATHWAYS after _classify_trend with exactly two pathways:

1. pathway_001 — Maintainer Departure Cascade
   - mechanism (full story): core maintainer stops → review slowdown → contributor decline
   - nodes checked in workshop code: maintainer_inactive, contributor_decline only
   - evidence_tier: 2, confidence_base: 0.55 (workshop weight, not calibrated)

2. pathway_002 — Release Drought
   - mechanism (full story): long gap without release → adoption stall → fork surge
   - nodes checked in workshop code: no_recent_release only
   - evidence_tier: 2, confidence_base: 0.45 (workshop weight, not calibrated)

analyze_causal_patterns(owner, repo) must:
- For pathway 001: check top contributor's last active week; compare unique contributors in the recent 13 weeks vs the prior 13 weeks
- For pathway 002: check days since the latest release (or flag if no releases)
- For each pathway, return: pathway name, mechanism, observations (per node with detected + detail), nodes_detected, nodes_checked, match_strength, evidence_tier, adjusted_confidence (confidence_base × match_strength), alternative_explanation
- Return a top-level dict with repository, pathways_checked, results, retrieved_at, and methodology noting Tier 2 pattern matching
- Return evidence only — do NOT pick which pathway "matters most"

_get_alternative(pathway_id) must return a competing explanation:
- pathway_001: seasonal slowdown (holidays, summer)
- pathway_002: intentional stability in a mature project

Use the existing gh client. Match the existing code style. Do not add new dependencies.
```

### What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, use the prompt above, then read this section to verify Cursor's output matches the intent.

**`CAUSAL_PATHWAYS`** is a list of hypothesized cause-effect chains in open-source projects. Each pathway's `mechanism` field describes the full story; the workshop code checks only the nodes listed in `nodes` (a deliberate simplification).

- **Pathway 001 — Maintainer Departure Cascade:** Mechanism claims maintainer drop-off → slower reviews → fewer contributors. **Checked in code:** top contributor inactive; unique contributors declined quarter-over-quarter.
- **Pathway 002 — Release Drought:** Mechanism claims long release gaps → adoption stall → fork surge. **Checked in code:** days since last release (or no releases found).

Each pathway includes an `id`, `name`, `mechanism`, `nodes` (what the code actually checks), `detection` rules, `evidence_tier` of 2, and a `confidence_base` score (**arbitrary workshop weight**, scaled by `match_strength` — not a calibrated probability).

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

### Evidence tiers (reminder for Part 3)

Your tools return **Tier 2** evidence. When the agent narrates causal claims, the system prompt should require naming the tier and including the alternative — and should not imply statistical proof or intervention-level certainty. Compliance is something you **evaluate**, not something Python enforces.

### Checkpoint

```bash
uv run --directory src python -c "from tools import analyze_causal_patterns; import json; print(json.dumps(analyze_causal_patterns('pallets', 'flask'), indent=2, default=str))"
```

**Success:** `pathways_checked: 2` with `observations` for each pathway.

### ADLC build note

You are **building guardrails into the data layer** — alternatives and evidence tiers are not optional niceties. They prevent overconfident agents.

---

## Part 3 · Test: Wire tools to Groq (13 min)

**ADLC phase: Test** — connect tools to the LLM, run the agent loop, and smoke-test behavior.

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
2. **Option B: Let Cursor write it** — Skip to [Option B](#option-b-let-cursor-write-it-2) and copy the prompt into Cursor chat.

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

# System prompt — your agent's rules
SYSTEM_PROMPT = """\
You are a project health analyst. You help users understand open-source
projects by combining quantitative metrics with causal reasoning.

RULES YOU MUST FOLLOW:

1. ALWAYS call get_repo_health first to get the data. Never guess metrics.

2. If any indicator flag is concerning, call analyze_causal_patterns to
   investigate why.

3. Never present a number without its reference context. "47 commits" is
   banned. "47 commits/week, 1.2 standard deviations below this project's
   historical average" is required.

4. For every causal claim, state the evidence tier (1-4) and acknowledge
   at least one alternative explanation.

5. When your evidence is Tier 1-2 (temporal or pattern), say "Based on
   observed patterns..." — NOT "Data proves..." or "This shows..."

6. Structure your response as a narrative briefing, not a bullet-point dump
   of raw data.
"""

> **Note:** `MUST` / `Never` in `SYSTEM_PROMPT` are **instructions to the model**, not guarantees enforced by Python. You still evaluate compliance in the Compare section.
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

### Option B: Let Cursor write it

1. In Cursor's file explorer, right-click the `src/` folder → **New File** → name it `agent.py` (the file can be empty).
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows) to open chat.
3. Copy the entire prompt below and paste it into chat. Press Enter.
4. Review the generated file before accepting. Run the checkpoint command when done.

**Cursor prompt (copy and paste):**

```
Create src/agent.py — a Groq function-calling agent for GitHub repository health analysis.

Imports and setup:
- import json, os, sys
- from dotenv import load_dotenv
- from groq import Groq
- from config import get_groq_model
- from tools import get_repo_health, analyze_causal_patterns
- load_dotenv()
- client = Groq(api_key=os.environ["GROQ_API_KEY"])
- MODEL = get_groq_model()  # do not hardcode a model name

Define TOOLS with two Groq function schemas: get_repo_health and analyze_causal_patterns.
Each needs owner and repo (required strings). Descriptions must explain what the tool returns AND state it does NOT return opinions or recommendations.

Define TOOL_FUNCTIONS mapping tool names to the Python functions.

Define SYSTEM_PROMPT with these rules:
1. Always call get_repo_health first — never guess metrics
2. If any indicator flag is concerning, call analyze_causal_patterns
3. Never present a number without reference context (z-scores, historical averages)
4. State evidence tier (1-4) for every causal claim
5. Acknowledge at least one alternative explanation
6. For Tier 1-2 evidence, say "Based on observed patterns..." not "Data proves..."
7. Structure the response as a narrative briefing, not a bullet dump

Implement run_agent(user_message):
- Agent loop: send messages to Groq with tools=TOOLS and model=MODEL
- If tool_calls returned, execute each function, append results, and loop
- Print each tool call like: [Calling get_repo_health({'owner': 'pallets', 'repo': 'flask'})]
- Return final text response when no more tool calls

Implement run_naive_agent(user_message):
- Same model, system prompt "You are a helpful assistant.", no tools

if __name__ == "__main__":
- Query from sys.argv or default to "Analyze the health of the pallets/flask repository."
- Print causal agent output, then naive agent output, with clear section headers

Match patterns used elsewhere in this project. Do not add new dependencies.
```

### What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, use the prompt above, then read this section to verify Cursor's output matches the intent.

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
- Naive agent often invents or guesses numbers — **that is the typical contrast** (re-run if your model happens to know the repo from pretraining)

### Try other repos

```bash
uv run src/agent.py "Analyze the health of facebook/react"
uv run src/agent.py "Should I contribute to psf/requests?"
```

### ADLC test note

You just **smoke-tested** the agent loop — tool calls fire, metrics come back with context. That is the **Test** phase: integration works. The full **Evaluate** phase comes later in [Compare: Causal vs naive agent](#compare-causal-vs-naive-agent-7-min), where you deliberately compare grounded vs ungrounded output.

Your pipeline mirrors a staged production design: `get_repo_health` (retrieve facts) → `analyze_causal_patterns` (structured evidence) → LLM (narrative only after data is in hand).

---

## Part 4 · Deploy: Package as an Agent Skill (8 min)

**ADLC phase: Deploy** — move capabilities from prototype into something others can use reliably.

Deployment connects your tools and reasoning rules to the environment where people actually work — not just proving the prototype runs. Packaging an [Agent Skill](https://agentskills.io) ships capability and rules together (`SKILL.md` + `scripts/tools.py`), decoupled from the core agent prompt — the same modular pattern production teams use for skills-based agents.

**Time tip:** Steps 1–4 fit the 8-minute block. Step 5 (in-chat demo) is optional — skip it if you are behind; terminal validation in step 4 is enough.

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

In Cursor's file explorer, right-click `.cursor/skills/repo-health-analyst/` → **New File** → name it `SKILL.md`.

The file starts with **YAML frontmatter** — metadata between `---` lines at the top. Cursor reads this to know when to activate the skill and what it needs to run:

- **`name`** identifies the skill in Cursor's skill list.
- **`description`** tells Cursor when to suggest this skill — it matches against what you type in chat.
- **`compatibility`** lists what must be installed for the skill to work.

**Copy and paste** the entire block below into `SKILL.md`:

````markdown
---
name: repo-health-analyst
description: >
  Analyze the health of a GitHub repository using causal reasoning. Use when
  asked to evaluate an open-source project, assess project health, check if a
  repo is well-maintained, investigate contributor risk, or decide whether to
  adopt or contribute to a project. Combines quantitative metrics with causal
  pathway analysis.
compatibility: Requires Python 3.11+, uv, and environment variables GITHUB_TOKEN and GROQ_API_KEY.
metadata:
  author: workshop-participant
  version: "1.0"
---

## What This Skill Does

Analyzes GitHub repository health by running two data tools and synthesizing
results with causal reasoning. The tools return structured data with indicator
flags — the agent provides interpretation and judgment.

## How to Use

1. Run the health check script to get metrics with reference context:

```bash
uv run python .cursor/skills/repo-health-analyst/scripts/tools.py health <owner> <repo>
```

2. If any indicator flags are concerning (`is_declining`, `has_bus_factor_risk`,
   `has_issue_backlog`), run the causal analysis:

```bash
uv run python .cursor/skills/repo-health-analyst/scripts/tools.py causal <owner> <repo>
```

3. Synthesize the results following these rules:

### Rules for Interpretation

- **Never present a number without its reference context.** "47 commits" is
  banned. "47 commits/week (z = -1.2 vs. 52-week self-history)" is required.
- **Every causal claim states its evidence tier:**
  - Tier 1 (temporal): "Following X, we observed Y..."
  - Tier 2 (pattern): "This matches a pattern seen in similar projects..."
  - Tier 3 (peer comparison): "Peer projects without X didn't show Y..."
  - Tier 4 (statistical): "Across N projects, X predicts Y (p < 0.05)..."
- **Every causal claim acknowledges an alternative explanation.** The tool
  returns one — include it.
- **Data functions return facts. You provide judgment.** The tool says
  `is_declining: true`. You decide whether that matters and why.
- **Structure output as a narrative briefing**, not a bullet-point data dump.

## Output Format

Present findings as a narrative briefing with these sections:
1. **Overview** — Repository identity, stars, activity level
2. **Health Assessment** — Metrics with reference context
3. **Causal Analysis** — Pathway matches with evidence tiers and alternatives
4. **Assessment** — Your synthesis based on all evidence
````

The `description` field is how Cursor decides when to activate your skill — write it carefully. You can edit the wording later; this version matches the tools you built in Parts 1–2.

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

#### 5. Test in Cursor (uses one Agent request)

This step is how you confirm the skill works *inside* Cursor — chat is what activates it. Open chat (**Cmd+L** / **Ctrl+L**) and ask:

> Analyze the health of pallets/flask

Cursor **may** load your skill, run your scripts, and follow your rules — if it does not, confirm the skill path and `description` in `SKILL.md`, or rely on the terminal tests in step 4.

**No chat quota left?** You already validated the skill in step 4 via the terminal. You can skip this step and still count Part 4 complete — you just will not see Cursor route through `SKILL.md` automatically.

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

Version your skill (`metadata.version` in frontmatter) — the same discipline as version pinning and rollback in production. Full deployment also integrates agents into business workflows (APIs, CRM, ticketing), defines fallbacks when tools fail, and monitors latency and task-completion rates after launch.

---

## Compare: Causal vs naive agent (7 min)

**ADLC phase: Evaluate** — behavioral comparison made visible, then map what you built to production.

This is the payoff for Part 3. You built two agents on the same query; now compare them side by side and close with how the same architecture scales beyond the workshop.

### Step 1 — Run both agents

From the project root:

```bash
uv run src/agent.py
```

Or try another repo:

```bash
uv run src/agent.py "Analyze the health of facebook/react"
```

Watch the terminal. The **causal agent** section should show `[Calling get_repo_health(...)]` (and possibly `analyze_causal_patterns`). The **naive agent** section has no tool calls.

### Step 2 — Open the comparison canvas

A **Cursor Canvas** is a live panel you can open beside chat — useful for structured side-by-side comparisons.

**Install the canvas template** (from the project root):

```bash
CANVAS_DIR="$HOME/.cursor/projects/Users-$(whoami)-Gitlab-causal-agent-workshop/canvases"
mkdir -p "$CANVAS_DIR"
cp docs/canvas/agent-comparison.canvas.tsx "$CANVAS_DIR/"
```

> **Can't find the folder?** In Cursor, open any `.canvas.tsx` file under your project's `.cursor/projects/.../canvases/` path, or ask your facilitator to share their screen — the terminal comparison in Step 1 is enough if canvas setup is blocked.

Open `agent-comparison.canvas.tsx` from the file explorer, then click **Open Canvas** in the editor tab to view it beside your terminal.

The canvas shows:

| | Causal agent | Naive agent |
|---|---|---|
| Data source | GitHub API (tool calls) | No tools — often guesses or pretraining recall |
| Context | z-scores, benchmarks | Raw numbers or guesses |
| Causal claims | Tier + alternatives | Unqualified assertions |

Plus abbreviated sample narratives so you know what *grounded* vs *ungrounded* output looks like.

### Step 3 — Discuss (2 min)

With your terminal output and the canvas open, answer as a group:

1. Did the naive agent quote any number the causal agent did not retrieve?
2. Did the causal agent state an evidence tier and an alternative?
3. Which briefing would you send to a colleague deciding whether to adopt the repo?

That three-question check is your evaluation harness — the simplest form of agent testing.

### Step 4 — From workshop to production (2 min)

What you built today maps to a production stack — same layers, different packaging:

| Layer | What you built | Production equivalent |
|-------|----------------|----------------------|
| Data intelligence | `tools.py` | Shared library or service — facts, flags, evidence tiers only |
| Tool-call / integration | `agent.py` `TOOLS` + dispatch | MCP server, API gateway, or host-native function calling |
| Orchestration | Groq loop + `SYSTEM_PROMPT` | Agent runtime — routing, guardrails, memory, fallbacks |
| Deploy | Agent Skill (`SKILL.md` + scripts) | Skills + MCP + workflow hooks (Slack, CRM, ticketing) |

**Agent runtime** — the orchestration row above. In Part 3, that is your `run_agent` loop: it calls the Groq API each turn, reads tool-call requests from the model, runs your Python functions, and appends results back into the conversation until the model returns a final answer. In production, the runtime is the same idea at larger scale — often a service or framework (LangGraph, custom Python, Cursor's agent host) that:

- **Invokes the LLM API** — sends messages, receives completions (inference happens on the provider's side; the runtime is the client)
- **Executes the tool loop** — parse tool calls, dispatch to MCP or local functions, feed results back
- **Applies guardrails** — system prompt, routing rules, max turns, policy checks
- **Handles failures** — retries, alternate model, graceful errors when Groq or GitHub is down

The runtime is the **conductor**, not the musician: it does not host model weights, and it is not your data layer (`tools.py`) or tool server (MCP). Token cost and latency are tracked here because this is where inference calls originate.

**MCP (Model Context Protocol)** — you may have heard this term. It standardizes how AI hosts (Cursor, Claude Desktop, internal platforms) discover and call external tools. In *this* architecture, MCP fits best at the **tool-call layer**: one server exposing `get_repo_health` and `analyze_causal_patterns` so every host shares the same governed API, auth, and audit trail. MCP does **not** replace what you learned today:

- The **data-intelligence boundary** still lives in your Python return shapes (no opinions in tools, evidence tiers in causal output).
- **Orchestration** still needs an agent loop, system prompt, and routing rules ("call health first, then causal if flags fire").
- **Skills** and MCP are complementary — a Skill carries *how to interpret* results; MCP carries *how to invoke* the tools.

**Other production essentials** (beyond what fits in 75 minutes):

- **Monitoring** — latency, task completion, tool-call failures, token cost
- **Evaluation suite** — test repos with expected flag values; rerun after prompt or model changes
- **Access control** — least-privilege tokens; deployed agents get their own identity and inherited permissions
- **Fallbacks** — what happens when GitHub rate-limits, Groq is down, or the model skips a tool call
- **Versioning** — pin model, prompt, and skill versions; rollback when behavior drifts

---

## Optional: Operate & monitor discussion (8 min)

*Skip this section in a 75-minute session unless you have extra time. The [Compare section](#compare-causal-vs-naive-agent-7-min) is the recommended wrap-up.*

**ADLC phase: Operate & monitor** — what happens after deploy once the agent is live.

ADLC does not end at deploy. Operate-and-monitor practices track latency, task completion, tool failures, and model drift, plus audits for permissions and compliance. Production agents also need visible reasoning (sources, not just answers), clear accountability (data owners maintain guidance; users own decisions), and access control that inherits existing permissions.

### Discussion questions (optional)

1. **The boundary test.** `is_declining` uses z-score < -1.0. Is the threshold a fact or a judgment? Where does the line fall?

2. **Evidence tiers.** What data would you need to move from Tier 2 (pattern) to Tier 3 (peer comparison)?

3. **Prompt sensitivity.** Remove one rule from `SYSTEM_PROMPT` and re-run. How much intelligence came from tools vs. instructions?

4. **Same data, different users.** How would you change the prompt (not the tools) for a CTO vs. a new contributor?

### What you would add for production (operate & monitor)

See [Step 4 — From workshop to production](#step-4--from-workshop-to-production-2-min) for the production architecture overview (layers, MCP, monitoring, access control). This optional section goes deeper on ongoing discipline:

- **Drift** — re-check when APIs, prompts, or model versions change
- **Accountability** — data owners maintain tool logic; users own decisions based on agent output
- **Compliance** — audit logs for tool calls, especially when agents access customer or internal data

ADLC does not end at deploy. Operate & monitor is the phase that keeps an agent trustworthy as requirements and models change.

---

## Reference card

### Project structure

After setup, the repo looks like this. Files you create during the workshop are marked with **← you create**.

```
causal-agent-workshop/
├── .venv/                             # ← created by uv sync (virtual environment)
├── docs/
│   ├── canvas/
│   │   └── agent-comparison.canvas.tsx  # Wrap-up comparison (install to Cursor canvases/)
│   └── workshop-guide.md              # This guide (ADLC-aligned)
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

Target behavior for the causal agent (enforce via prompts and evaluation, not Python alone):

1. Do not present a number without reference context.
2. Do not let a data function return opinions.
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
