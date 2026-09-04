# Workshop Guide

**Build an Intelligence Agent, Not a Chatbot**

> *Not what happened. Why it happened. What happens next.*

A 75-minute hands-on workshop on building agents that reason about data — not just repeat it.

## Start here — setup and session prep (5 min)

If you already completed the [pre-workshop setup](../README.md), run through steps 1–2 to sync files and verify GitHub + Groq access. Step 3 helps you decide how to use Cursor AI before the hands-on sections.

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

`git pull` **failed?** Fetch and reset your branch to match the remote (this **discards uncommitted changes** in this repo):

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

Open `src/tools.py`. You will implement the functions marked `NotImplementedError` during the two **Build** sections.

**Stuck?** See [README troubleshooting](../README.md#troubleshooting).

### 3. How you will work in Cursor

Before the hands-on sections, decide how much you will rely on Cursor AI — especially on the **free tier**, where Plan and Agent sessions are limited.

**Default path (recommended for live sessions):** paste the working code from this guide. Every section includes complete blocks for `src/tools.py`, `agent.py`, and the Agent Skill. No AI credits required, and the room stays on schedule.

**If you want to use Cursor AI**, spread sessions across the workshop rather than spending them all in the first **Build** section:

- **Plan** — try [Plan mode](https://cursor.com/docs/agent/plan-mode) once to draft an implementation plan before you code (see [Plan: Scope the repo health agent](#plan-scope-the-repo-health-agent-8-min)). Review the plan as a group; do not click **Build** unless you intend to let Cursor write code for you in **Build** or **Test**.
- **Build + Test** — each section also includes an optional prompt so Cursor can implement the exercise instead of paste; that typically costs an Agent session per section. In a live session, **pair up**: one person pastes reference code, the other tries Cursor, or swap roles between sections.
- **Deploy** — save one Agent chat to test your packaged skill in Cursor.

You can mix approaches — paste some parts, delegate others. The reference code is always there to fall back on or to diff against Cursor's output.

---

## What this workshop teaches

Many agent demos retrieve a metric and summarize it — users still ask *so what?* This workshop builds **intelligence agents**: tools that return auditable facts with context, plus reasoning rules for plausible *why* and honest confidence. The causal framework — Pearl's ladder, evidence tiers, pathway templates — is developed in [Build: Causal reasoning](#build-causal-reasoning-17-min) when you implement `analyze_causal_patterns`.

### What you will have at the end

A small agent that:

1. **Pulls real data** from GitHub (not guesses)
2. **Adds context** to every metric (benchmarks, trends, flags)
3. **Reasons causally** with evidence tiers and alternative explanations (when the model follows the rules)
4. **Packages as a portable Agent Skill** for Cursor and other tools

### How this differs from traditional machine learning

Traditional ML is built to **predict** — given inputs, produce a score or label trained on historical examples. That works well when you have lots of labeled data, a stable problem, and users who only need the prediction itself.


|                    | Traditional ML                                                          | This workshop's approach                                       |
| ------------------ | ----------------------------------------------------------------------- | -------------------------------------------------------------- |
| **Primary output** | A score or class ("73% churn risk")                                     | Structured facts + narrative reasoning                         |
| **Training**       | Collect data, engineer features, train, validate, deploy                | No model training — you write tools and prompts                |
| **"Why?"**         | Often opaque; explainability is a separate project                      | Designed in: baselines, pathways, evidence tiers, alternatives |
| **Causation**      | Usually learns correlation; true causality needs extra methods and data | Explicit causal templates + honest confidence labels           |
| **Adaptability**   | New questions often mean new features or retraining                     | Same tools; the LLM adapts answers to the user's question      |
| **Best at**        | High-volume pattern matching at scale                                   | Interactive analysis where context and explanation matter      |


Neither replaces the other. Production systems often use **both**: ML for scoring at scale, agents for interpretation, investigation, and communication. The mistake is treating a general-purpose LLM chatbot as a substitute for either — it has no **domain-specific fitted model** for your data and no structured evidence layer unless you build one.

This workshop focuses on that missing layer: **tools that return auditable facts**, plus **reasoning rules** that force the agent to contextualize metrics, separate correlation from mechanism, and admit uncertainty.

### Design patterns for intelligence agents (not chatbots)

These patterns show up when an agent must support real decisions. They are design choices, not laws — illustrated here and in Red Hat's [enterprise data agent](https://www.redhat.com/en/blog/we-built-enterprise-data-agent-and-you-can-too) write-up:

1. **Metrics without baselines are noise.** A number only becomes a signal when it is compared to something — history, peers, or expected range. Agents that quote raw counts feel confident and mislead.
2. **Correlation is not an explanation.** Two trends moving together does not mean one caused the other. Useful agents separate *what we observe* from *why we think it happened* — and label how strong that evidence is.
3. **Facts and judgment should stay separate.** Structured data functions should return indicator flags and reference context, not recommendations. The LLM interprets for the user's situation; if opinions are baked into the data layer, the same tool breaks for every role.
4. **Overconfidence is worse than uncertainty.** Strong agents acknowledge alternative explanations and state evidence tier — especially when reasoning from patterns rather than controlled experiments.
5. **The data-intelligence boundary scales.** One well-designed tool layer can serve many prompts, personas, and workflows. The intelligence layer adapts; the data layer stays auditable.

Agents can fail when they guess without sources, when business context is missing, and when data and judgment are mixed. Production teams address that with a **data foundation** (one source of truth per domain), a **guidance architecture** (routing rules and documentation the LLM consults before answering), a **staged pipeline** (retrieve → narrow → reason → return, with each step logged), and **skills-based packaging** (capabilities and rules as modular documents the agent loads on demand). Trust, accountability, and inherited access control matter as much as model choice.

---

## ADLC: How this workshop is structured

**ADLC** (Agent Development Lifecycle) is an emerging industry trend for building and operating AI agents in real workflows — analogous to how SDLC structures traditional software delivery. Vendors and teams define the phases differently; there is no single standard yet. **This workshop uses [IBM's ADLC framework](https://www.ibm.com/think/topics/agent-development-lifecycle-adlc)** as its organizing model:

**plan → build → test → deploy → operate → monitor**

Traditional software (**SDLC**) is deterministic: the same input yields the same output, and failures usually crash or throw obvious errors. Agents are probabilistic: the same prompt can yield different answers, and failures often look plausible — a confident wrong answer is harder to spot than a stack trace. ADLC addresses that shift through behavioral evaluation, guardrails, and ongoing monitoring rather than ship-once-and-forget.

### How the workshop maps to ADLC

This workshop covers **plan through deploy** in 75 minutes, plus **evaluate** as the wrap-up. **Operate & monitor** is optional reading after the session.

**Running behind?** Focus on **Test** — that is where the agent comes alive. The two **Build** sections are the foundation; **Deploy** is packaging what you already built. Skip the optional [Operate & monitor appendix](#optional-operate--monitor-discussion-8-min) if you are short on time.


| IBM ADLC phase        | Workshop section                  | What you produce                                                                           |
| --------------------- | --------------------------------- | ------------------------------------------------------------------------------------------ |
| **Plan**              | Plan: Scope the repo health agent | Problem scope, success criteria, Cursor plan                                               |
| **Build**             | Build: Data tools + Build: Causal reasoning | `tools.py` — facts, flags, causal evidence                                                 |
| **Test**              | Test: Wire tools to Groq                    | `agent.py` — agent loop wired and smoke-tested                                             |
| **Deploy**            | Deploy: Package as an Agent Skill           | Agent Skill (`SKILL.md` + scripts)                                                         |
| **Evaluate**          | Evaluate: Causal vs naive agent             | Behavioral comparison + production architecture *(workshop label — not an IBM phase name)* |
| **Operate & monitor** | Optional appendix (end of guide)  | Drift, accountability, compliance — after launch                                           |

---

## Plan: Scope the repo health agent (8 min)

**plan** → build → test → deploy → operate → monitor

Nail down what you are building, where facts end and judgment begins, then practice **Plan mode** in Cursor before any code.

*~4 min on scope and the data-intelligence boundary, then ~4 min in Plan mode.*

### The problem we are solving

**User scenario:** A developer is about to invest real time in an open-source project — adopting it as a dependency, or contributing their first pull request — and needs to judge **project health** before committing. Are commits and contributors holding steady or sliding? Are maintainers still active? If something looks off, is there a plausible explanation — or a reason to walk away?

Typical questions sound like: *"Should I contribute to `pallets/flask`?"* or *"Can we ship `psf/requests` as a production dependency — is it still actively maintained?"* The hard part is not getting an answer — it is getting one **grounded in current data**, not training-memory guesses.

This workshop builds a **repo health analyst** that pulls live GitHub metrics and structures the reasoning:


| Piece          | What it does                                                                                   | Where you build it     |
| -------------- | ---------------------------------------------------------------------------------------------- | ---------------------- |
| **Data tools** | Pull live metrics, add benchmarks and flags, return causal pathway matches with evidence tiers | `tools.py` (Build)     |
| **Agent loop** | Call tools, synthesize a narrative briefing                                                    | `agent.py` (Test)    |
| **Packaging**  | Ship capability + interpretation rules for reuse                                               | Agent Skill (Deploy)   |


That table is the high-level scope for the session. Planning means turning it into a design: what each tool returns, what the LLM is allowed to infer, and how you will know the agent succeeded.

### Where to draw the line

The [design patterns](#design-patterns-for-intelligence-agents-not-chatbots) above apply directly to this agent. For `tools.py` vs the LLM:


| Data layer (`tools.py`)                    | Intelligence layer (LLM + prompts)                 |
| ------------------------------------------ | -------------------------------------------------- |
| Numbers, flags, z-scores                   | What those numbers mean for the user               |
| Historical benchmarks                      | Whether a deviation matters given relevant context |
| Causal pathway evidence                    | Which explanation best fits the evidence           |
| Methodology notes ("Tier 2 pattern match") | Narrative synthesis                                |


**Think about it:** What is the LLM using to make each judgment in the right column? What happens if the left column is missing or wrong?

**Rule of thumb:** If it could be wrong in a spreadsheet, it belongs in Python. If it requires judgment, it belongs in the LLM — but only if the data layer supplies the facts and context to judge from.

### Success criteria (your plan should cover these)

- **Inputs:** GitHub `owner` + `repo` (e.g. `pallets/flask`)
- **Outputs:** Structured tool results plus a narrative briefing the user can act on
- **Success (target behavior):** The agent does not quote a metric unless a tool returned it; causal claims include an evidence tier and an alternative explanation (you verify this in [Evaluate](#evaluate-causal-vs-naive-agent-7-min))

---

### Try it: Plan in Cursor (~4 min)

You have the problem, scope, and boundary. Next step in ADLC is to turn that into a **reviewable implementation plan** before any code runs. Cursor **[Plan mode](https://cursor.com/docs/agent/plan-mode)** is built for that — it researches the repo, can ask clarifying questions, and produces a plan you can edit or reject.

#### Steps

1. Open Cursor chat (`Cmd+L` / `Ctrl+L`).
2. Press `Shift+Tab` from the chat input (or use the **mode picker**) until the mode shows **Plan**.
3. Copy the prompt below, paste it into chat, and press **Enter**.
4. Answer any clarifying questions Cursor asks (pick sensible defaults if you are unsure).
5. When the plan appears, read it — especially which work belongs in `tools.py` vs. the LLM.

**Do not click Build yet.** The learning goal is to **review the plan** against the scope and boundary above. Build switches to Agent mode and starts editing files — save that for [Option B](#option-b-let-cursor-write-it) in **Build** or **Test** if you want.

> **Facilitator tip:** See [Start here — step 3](#3-how-you-will-work-in-cursor) for how participants should budget Cursor AI. In a live session, demo Plan mode on one screen while the room discusses the plan. Pairs work too: one partner runs Plan mode, the other scores the plan against the boundary table above.

#### Copy-paste prompt

```
Plan how to implement this workshop's GitHub repo health agent (causal-agent-workshop).

Before any code, produce a structured implementation plan that covers:

1. Problem, inputs, outputs, and success criteria (measurable — e.g. no hallucinated metrics)
2. Data layer (src/tools.py): what each tool returns — facts, flags, z-scores, evidence tiers only; explicitly what must NOT be returned (opinions, recommendations, severity labels)
3. Intelligence layer: system prompt rules, evidence tiers, when to call which tool
4. Files and order of work (Build → Test → Deploy)
5. Risks and guardrails (overconfidence, correlation vs causation, token/API limits)

Read the existing stubs in src/tools.py and the workshop structure in docs/workshop-guide.md for context.

Planning only — do not implement or edit files yet.
```

#### Review the plan (2 min)

With the plan open, check as a group (or with your partner):

1. Does the plan keep **facts in `tools.py`** and **judgment in the LLM** — matching the boundary table?
2. Are success criteria **testable** (not vague like "good answers")?
3. What would you change before clicking **Build**?

Optional: click **Save to workspace** on the plan file so you can reference it during **Build**, **Test**, and **Deploy**.

#### Connect to the rest of the workshop


| Path                   | What you do                                                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Default (Option A)** | Copy the working code from this guide in **Build** and **Test** — compare your mental model to the plan you just reviewed                                                 |
| **Option B**           | Return to your plan in **Build** or **Test** and click **Build** on the relevant steps, or start a fresh Plan for each section — then diff Cursor's output against Option A |


Either way, the plan is the contract. The code is the implementation.

---

### How Build and Test work

Each section gives you two ways to implement the code:

- **Option A: Copy the code** — A complete, working code block you paste into `src/tools.py`. This gets you running immediately so you can focus on understanding.
- **Option B: Let Cursor write it** — Copy the ready-made prompt for that section into Cursor chat (`Cmd+L` / `Ctrl+L`). Cursor will edit the file for you. Compare what it generates to the working code in Option A.

You can do both — paste the code first, then read the description and try Option B to see how Cursor's version compares. This is how you learn to evaluate AI-generated code against a known-good reference.

---

## Build: Data tools with context (17 min)

plan → **build** → test → deploy → operate → monitor

Implement the data layer with clear boundaries.

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

The file already has imports, `load_dotenv()`, and `gh = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))`. Replace the `NotImplementedError` stubs only — do not rewrite the whole file.

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


| Flag                  | True when...                 |
| --------------------- | ---------------------------- |
| `is_active`           | Recent weekly average > 0    |
| `is_declining`        | z-score < -1.0               |
| `has_bus_factor_risk` | Top contributor share > 50%  |
| `has_issue_backlog`   | More open than closed issues |


`_classify_trend(weekly)` classifies the commit trend by splitting the weekly list in half and comparing the averages:


| Condition                      | Label               |
| ------------------------------ | ------------------- |
| Fewer than 8 weeks             | `insufficient_data` |
| Second half / first half > 1.2 | `accelerating`      |
| Ratio > 0.9                    | `stable`            |
| Ratio > 0.6                    | `slowing`           |
| Otherwise                      | `declining`         |


### Checkpoint

```bash
uv run --directory src python -c "from tools import get_repo_health; import json; print(json.dumps(get_repo_health('pallets', 'flask'), indent=2, default=str))"
```

**Success:** JSON output with `metrics`, `indicator_flags`, and a numeric `z_score`.

### ADLC build note

You just defined the **contract** for your data layer. Every consumer of `get_repo_health` — different prompts, different users — gets the same facts. That is how you build agents that scale beyond a single demo. In production, teams call this **data product ownership**: one source of truth, maintained by people who know the domain.

---

## Build: Causal reasoning (17 min)

plan → **build** → test → deploy → operate → monitor

Add structured evidence the LLM can reason over.

**File:** `src/tools.py` (same file)  
**Functions:** `analyze_causal_patterns`, `_get_alternative`

### Why correlation is not enough

[Build: Data tools](#build-data-tools-with-context-17-min) answered **what** is happening — metrics with baselines and flags. This section asks **why**, but only from **observational** GitHub data: timelines, issue counts, contributor stats. You watch repos over time; you do not run a controlled experiment. When two trends move together in that setting, you have **association** — they co-occur. That is not the same as showing one caused the other.

**Why not?** Because of **confounding**: you often cannot tell whether A caused B, or whether something else explains both. Commits fall while a maintainer steps back — the maintainer may have driven the drop, or a holiday quarter, a platform outage, or a scope shift could explain the same pattern. Until you can rule out those alternatives, any *why* claim stays **unidentified**, no matter how convincing it sounds.

LLMs will narrate a *why* anyway — fluently, from thin evidence. This **Build** section does not solve causal identification on GitHub logs; it **structures** the reasoning so the agent stays honest. You will build **pathway templates** (hypothesized mechanisms), require **competing explanations** on every match, and label **evidence tiers** (how strong the claim is). The sections below define that framework; then you implement it in `analyze_causal_patterns`.

### Pearl's ladder — three types of "why" questions

**Judea Pearl** (*[The Book of Why](https://en.wikipedia.org/wiki/The_Book_of_Why)*) separates three question types. Each rung needs stronger assumptions than the last:


| Rung                  | Question                | Example                                                         | This workshop                                              |
| --------------------- | ----------------------- | --------------------------------------------------------------- | ---------------------------------------------------------- |
| **1. Association**    | What co-occurs?         | "Ice cream sales and drowning deaths both rise in summer"       | **Yes** — both **Build** sections use observational GitHub data only     |
| **2. Intervention**   | What if we *do* X?      | "If we run the ad campaign, will sales go up?"                  | **No** — needs experiments or special study designs        |
| **3. Counterfactual** | What if X had differed? | "Would this patient have recovered if they had taken the drug?" | **No** — needs a full structural model of cause and effect |


GitHub logs keep you on **rung 1**.

> **Resource:** [Causal AI: How cause and effect will change artificial intelligence](https://www.spglobal.com/en/research-insights/special-reports/causal-ai-how-cause-and-effect-will-change-artificial-intelligence) (S&P Global) — industry perspective on moving beyond correlation in AI systems.

### Evidence tiers — how strong is the claim?

On rung 1, not all observational claims are equally supported. This workshop uses four **evidence tiers** — a rubric for how much an agent can justify from GitHub data alone:


| Tier | Strength          | How to phrase it                                |
| ---- | ----------------- | ----------------------------------------------- |
| 1    | Temporal sequence | "Following X, we observed Y..."                 |
| 2    | Pattern match     | "This matches a known pattern..."               |
| 3    | Peer comparison   | "Peer projects without X didn't show Y..."      |
| 4    | Statistical test  | "Across N projects, X predicts Y (p < 0.05)..." |


**Higher tier = stronger evidence.** Tier 1 is the weakest (sequence alone); Tier 4 is the strongest (tested across many cases). None of these tiers prove causation on their own — they rank how much observational support an agent can claim.

> **Workshop scope:** `analyze_causal_patterns` returns **Tier 2** evidence only. Tiers 3–4 are in the rubric so the agent can narrate honestly — do not claim Tier 3 or 4 unless you build tools that produce peer comparisons or statistical tests.


| If the agent says…                                               | Supported by observational data (Rung 1)?                            |
| ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| "Following maintainer inactivity, we observed declining commits" | Yes — Tier 1 (temporal sequence)                                     |
| "This matches a maintainer-departure cascade pattern"            | Yes — Tier 2 (pattern match)                                         |
| "Adding a maintainer would restore velocity"                     | **No** — implies intervention (Rung 2), not supported by GitHub logs |
| "The decline would not have happened without burnout"            | **No** — implies counterfactual (Rung 3), not supported by GitHub logs |


### The methodology — what you will build

This section implements a four-step process the agent will use in **Test**:

1. **Hypothesize** — Define **pathway templates** in `CAUSAL_PATHWAYS`: plain-English stories of how decline might happen (e.g. maintainer leaves → fewer contributors).
2. **Match** — `analyze_causal_patterns` checks whether repo data fits signals in each template (using metrics from the previous Build section). This is **pattern matching**, not proof.
3. **Compete** — Every match returns an `alternative_explanation` — another story that could explain the same signals.
4. **Label** — Return the evidence tier (Tier 2) so the LLM states how strong the claim is.

That is **abductive** reasoning: the best-fitting story under constraints — not causal identification. A seasonal slowdown could fit the same signals as a maintainer departure; the alternative and tier make that uncertainty explicit.

**Extension:** See [Beyond rung 1](#beyond-rung-1--discussion) at the end of this section for how you would build toward intervention and counterfactual claims.

### Two ways to implement

Same choice as [Build: Data tools](#build-data-tools-with-context-17-min):

1. **Option A: Copy the code** — Paste the working code below into `src/tools.py`.
2. **Option B: Let Cursor write it** — Skip to [Option B](#option-b-let-cursor-write-it-1) and copy the prompt into Cursor chat.

### Option A: The code

Still in `src/tools.py`, replace the `analyze_causal_patterns` and `_get_alternative` stubs with the code block below (which includes `CAUSAL_PATHWAYS`, `analyze_causal_patterns`, and `_get_alternative`), pasted after `_classify_trend`:

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
            "maintainer_inactive": "Top contributor had 0 commits in the most recent week",
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
            "alternative_explanation": (
                _get_alternative(pathway["id"]) if nodes_detected > 0 else None
            ),
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

1. Open `src/tools.py` in Cursor (your data-tools functions should already be in place).
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows) to open chat.
3. Copy the entire prompt below and paste it into chat. Press Enter.
4. Review the changes before accepting — make sure it adds `CAUSAL_PATHWAYS` and implements `analyze_causal_patterns` and `_get_alternative`.

**Cursor prompt (copy and paste):**

```
Implement causal reasoning in src/tools.py: CAUSAL_PATHWAYS, analyze_causal_patterns, and _get_alternative.

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
- For each pathway, return: pathway name, mechanism, observations (per node with detected + detail), nodes_detected, nodes_checked, match_strength, evidence_tier, adjusted_confidence (confidence_base × match_strength), alternative_explanation (competing explanation if nodes detected, else None)
- Return a top-level dict with repository, pathways_checked, results, retrieved_at, and methodology noting Tier 2 pattern matching
- Return evidence only — do NOT pick which pathway "matters most"

_get_alternative(pathway_id) returns a competing explanation for detected pathways:
- pathway_001: seasonal slowdown (holidays, summer)
- pathway_002: intentional stability in a mature project

Use the existing gh client. Match the existing code style. Do not add new dependencies.
```

### What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, use the prompt above, then read this section to verify Cursor's output matches the intent.

`CAUSAL_PATHWAYS` defines hypothesized cause-effect chains in open-source projects. Each pathway includes an `id`, `name`, a narrative `mechanism`, an `evidence_tier` (Tier 2), a `confidence_base` (an arbitrary workshop weight scaled by match strength, not a calibrated probability), and `nodes` representing the subset of signals checked in code:

- **Pathway 001 — Maintainer Departure Cascade:** Hypothesizes maintainer drop-off → slower reviews → fewer contributors. **Checked in code:** top contributor inactive in recent week; unique contributors declined quarter-over-quarter.
- **Pathway 002 — Release Drought:** Hypothesizes long release gaps → adoption stall → fork surge. **Checked in code:** days since last release (or no releases found).

`analyze_causal_patterns(owner, repo)` checks those pathways against real data from the repository. For each pathway, it builds a result with: per-node `observations` (detected or not, with detail strings), counts of `nodes_detected` vs. `nodes_checked`, a `match_strength` ratio, the `evidence_tier`, an `adjusted_confidence` (base confidence scaled by match strength), and an `alternative_explanation` (when nodes are detected).

The function returns evidence, not conclusions. It does **not** pick a "winner" pathway — that is the LLM's job.

`_get_alternative(pathway_id)` returns a competing explanation for each pathway when signals are detected. Every causal claim must acknowledge at least one alternative:

- Pathway 001: seasonal slowdown (holidays, summer)
- Pathway 002: intentional stability in a mature project

### Checkpoint

```bash
uv run --directory src python -c "from tools import analyze_causal_patterns; import json; print(json.dumps(analyze_causal_patterns('pallets', 'flask'), indent=2, default=str))"
```

**Success:** `pathways_checked: 2` with `observations` for each pathway.

### Beyond rung 1 — discussion

This workshop stays on Pearl's **association rung** — observational GitHub data, pattern matching, Tier 2 evidence. Rungs 2 and 3 need different **data**, **design**, and **tools**, but the same architecture: facts in `tools.py`, strength labels and alternatives in the output, judgment in the LLM.

**Rung 2 — Intervention ("What if we *do* X?")**

To support intervention claims, the agent needs evidence from a **change you can attribute to an action**, not just co-occurrence. Classical study designs and **causal ML** methods both belong in the tool layer — fitted offline or via a service, with results returned as structured facts:


| Approach                                      | Example in open-source health                                                                                                              | What you might add                                                                                                    |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| **Randomized experiment**                     | Assign repos to a maintainer-onboarding program; compare outcomes                                                                          | A tool that reads experiment assignment + pre/post metrics                                                            |
| **Natural experiment**                        | A maintainer returns after a long absence; compare activity before vs. after                                                               | Event-study or before/after tool with a clear intervention date                                                       |
| **Quasi-experiment (diff-in-diff, matching)** | Repos that joined a foundation vs. matched peers; or a platform policy change with pre/post trends                                         | A tool returning `ate`, `confidence_interval`, and design assumptions (e.g. parallel trends)                          |
| **Causal ML (DML, causal forests)**           | Thousands of repos with many confounders — estimate effect of an action on repos matching a target profile (e.g. adding `CODEOWNERS`) | Fitted model in a tool returning `ate` or `cate` (effect for this repo's cohort), `method`, and assumptions |


> **Diff-in-diff (footnote):** Compare how much the outcome *changed* in a treated group vs. a control group over the same period. Mental model: `(after − before)_treated − (after − before)_control` — an estimate of the intervention effect if both groups would have trended in parallel without the action.

> **Causal ML (footnote):** Traditional ML predicts outcome *Y* from repo features (prone to correlation traps). Causal ML estimates the **effect of an action** on repos matching a target profile—controlling for dozens of confounding variables that make simple "twin repo" matching impossible. It estimates the **conditional treatment effect** (Pearl's **do(X)** for this cohort): *"For repos that look like ours, what is the expected lift from action X?"* ML controls for the confounders; the causal design isolates the effect.

**Rung 3 — Counterfactual ("What if X had been different?")**

To support counterfactual claims, the agent needs evidence from a **modeled estimate of what would have happened**, not just an intuitive narrative (e.g. *"Without burnout, velocity would have stayed high"*). Because an alternate history cannot be observed directly, tools construct the counterfactual using auditable data—historical baselines, unaffected peer repos that tracked the project before the event (a "donor pool"), or fitted structural equations. The tool computes the hypothetical outcome and returns the empirical assumptions required for it to hold; the LLM communicates both the estimate and its caveats:


| Approach                         | Example in open-source health                                                                                                                                           | What the tool outputs & assumes                                                                                                                         |
| -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Historical baseline scenario** | When the top maintainer was last active, commits averaged 12/week; now 4/week — gap if activity had stayed at the prior level                                           | Returns `observed`, `baseline`, and `gap` — assumes steady-state velocity absent seasonal variation or project maturity                                 |
| **Matched-repo comparison**      | A similar project without maintainer loss kept velocity flat while this repo dropped                                                                                    | Returns peer trajectory delta — assumes the matched project shared identical ecosystem exposure and contributor demand                                  |
| **Synthetic control**            | Build a custom "clone" of this specific repo by weighting a pool of peer repos that didn't lose a maintainer, tracking the path this repo would have taken             | Returns `observed_vs_synthetic`, `donor_weights` (the weights given to each unaffected peer), and pre-event fit error — proves the weighted pool accurately tracked this repo *before* the event |
| **Structural model (SCM / DAG)** | Pathway 001 as a **DAG**: maintainer activity → review latency → contributors → commits; estimate links, then query hypotheticals (the graph makes assumptions visible) | Returns a predicted outcome range from fitted equations — assumes no unobserved confounders exist between graph nodes                                   |


**What stays the same**


| Workshop today                             | Rungs 2–3 in production                                                                      |
| ------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `tools.py` returns facts, not opinions     | New tools for experiments, cohorts, or fitted causal estimates                               |
| Evidence tiers label strength              | Explicit evidence labels (e.g. identified ATE, model assumptions, or Tier 3–4 peer cohorts)  |
| `alternative_explanation` on every pathway | Competing models or assumptions, not just competing stories                                  |
| LLM synthesizes; Python does not judge     | Same data-intelligence boundary                                                              |


---

## Test: Wire tools to Groq (13 min)

plan → build → **test** → deploy → operate → monitor

Connect tools to the LLM, run the agent loop, and smoke-test behavior.

**File:** Create `src/agent.py`

### What you are building

An **agent loop:**

```
User question → LLM decides which tools to call → your Python runs → LLM synthesizes answer
```

Plus a **naive agent** with no tools — for comparison in [Evaluate](#evaluate-causal-vs-naive-agent-7-min).

### Two ways to implement

Same choice as the **Build** sections:

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
# from langfuse import get_client, observe

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
   at least one alternative explanation. For detected pathways or observed
   symptoms, weigh the hypothesized mechanism against plausible competing
   explanations (e.g. intentional API stability, seasonal variation) before
   drawing conclusions. Do not cite alternative explanations for pathways
   that were not detected.

5. When your evidence is Tier 1-2 (temporal or pattern), say "Based on
   observed patterns..." — NOT "Data proves..." or "This shows..."

6. Structure your response as a narrative briefing, not a bullet-point dump
   of raw data.
"""

# Note: MUST / Never in SYSTEM_PROMPT are instructions to the model, not
# guarantees enforced by Python. You still evaluate compliance in Compare.

# Optional Langfuse tracing (ADLC operate/monitor). Leave commented for the workshop.
# To enable: uncomment the langfuse import above, the three @observe lines, and flush() below.
# Env: LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
#
# @observe(name="groq-chat", as_type="generation")
def groq_chat(**kwargs):
    return client.chat.completions.create(**kwargs)


# Agent loop — LLM decides which tools to call, Python runs them, LLM synthesizes
# @observe(name="causal-agent")
def run_agent(user_message: str) -> str:
    """Run the full agent loop: user -> LLM -> tools -> LLM -> response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = groq_chat(
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
                print(f"  Calling {fn_name}({fn_args})")

                tool_fn = TOOL_FUNCTIONS.get(fn_name)
                result = tool_fn(**fn_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })
        else:
            return msg.content


# Naive agent — no tools, no rules, for comparison
# @observe(name="naive-agent")
def run_naive_agent(user_message: str) -> str:
    """A naive agent with no tools and no reasoning rules — for comparison."""
    response = groq_chat(
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
    # get_client().flush()
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

Include this commented-out Langfuse import (leave it commented; do not import langfuse as live code):
- # from langfuse import get_client, observe

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

Add a thin Groq wrapper (live) so you can later put @observe on it — you cannot decorate an inline method call:
- def groq_chat(**kwargs): return client.chat.completions.create(**kwargs)
- Above it, commented: Optional Langfuse tracing (ADLC operate/monitor). Leave commented for the workshop.
- Commented: To enable: uncomment the langfuse import, the three @observe lines, and flush() below.
- Commented: Env: LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
- Commented decorator: @observe(name="groq-chat", as_type="generation")

Implement run_agent(user_message):
- Commented decorator: @observe(name="causal-agent")
- Agent loop: send messages via groq_chat with tools=TOOLS and model=MODEL
- If tool_calls returned, execute each function, append results, and loop
- Print each tool call like: `Calling get_repo_health({'owner': 'pallets', 'repo': 'flask'})`
- Return final text response when no more tool calls

Implement run_naive_agent(user_message):
- Commented decorator: @observe(name="naive-agent")
- Same model via groq_chat, system prompt "You are a helpful assistant.", no tools

if __name__ == "__main__":
- Query from sys.argv or default to "Analyze the health of the pallets/flask repository."
- Print causal agent output, then naive agent output, with clear section headers
- Commented: get_client().flush()

Match patterns used elsewhere in this project. Do not add new dependencies. Leave all Langfuse lines commented.
```

### What that code does (in plain English)

If you chose Option A, read through this to understand what you pasted. If you chose Option B, use the prompt above, then read this section to verify Cursor's output matches the intent.

**Imports and setup.** Import `json`, `os`, `sys`, `dotenv`, `Groq`, `get_groq_model` from `config.py`, and the two tool functions from `tools.py`. Load `.env`, create the Groq client, and set `MODEL = get_groq_model()`. The default model is `openai/gpt-oss-20b`; set `GROQ_MODEL=qwen/qwen3.6-27b` in `.env` to use Qwen instead.

**Tool schemas (**`TOOLS`**).** Define two function schemas in Groq's function-calling format. Each has a `name` (matching the Python function), a `description` that says what the tool returns *and* what it does not return, and `parameters` for `owner` and `repo` (both required strings). The descriptions are guardrails — saying "Does NOT return opinions" keeps the data-intelligence boundary intact.

**Tool function map (**`TOOL_FUNCTIONS`**).** A dictionary mapping tool name strings to the actual Python functions.

**System prompt (**`SYSTEM_PROMPT`**).** This is where you decide how the agent should behave. Think about what you learned in both **Build** sections: the data layer returns facts with context, evidence tiers, and alternative explanations. The system prompt should tell the LLM how to use all of that responsibly. Consider: When should the agent call each tool? How should it present numbers? How should it handle uncertainty? What should it never do?

**Agent loop (**`run_agent`**).** Takes a user message, puts it in a messages list with the system prompt, and loops: send messages through `groq_chat` with `tools=TOOLS`, if the model requests tool calls then run each Python function and append the results to messages, otherwise return the text response. Use `model=MODEL`. Print each tool call so you can see what happened.

**Naive agent (**`run_naive_agent`**).** Same model via `groq_chat`, but with a generic system prompt ("You are a helpful assistant") and no tools. This exists for comparison — to show the difference between an agent with structured data and one without.

**Optional tracing.** You cannot put `@observe` on an inline method call, so `groq_chat` is a three-line wrapper around `client.chat.completions.create`. The Langfuse import, `@observe` decorators, and `get_client().flush()` are commented out — leave them that way for the workshop; the agent does not need Langfuse to run. To turn tracing on later: set `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_HOST` in `.env`, then uncomment those lines. In Langfuse, open the nested **groq-chat** generation — the model's `tool_calls` are on that span's output.

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

You just **smoke-tested** the agent loop — tool calls fire, metrics come back with context. That is the **Test** phase: integration works. The **Evaluate** payoff is in [Evaluate: Causal vs naive agent](#evaluate-causal-vs-naive-agent-7-min), where you compare grounded vs ungrounded output.

Your pipeline mirrors a staged production design: `get_repo_health` (retrieve facts) → `analyze_causal_patterns` (structured evidence) → LLM (narrative only after data is in hand).

---

## Deploy: Package as an Agent Skill (8 min)

plan → build → test → **deploy** → operate → monitor

Move capabilities from prototype into something others can use reliably.

Deployment connects your tools and reasoning rules to the environment where people actually work — not just proving the prototype runs. Packaging an [Agent Skill](https://agentskills.io) ships capability and rules together (`SKILL.md` + `scripts/tools.py`), decoupled from the core agent prompt — the same modular pattern production teams use for skills-based agents.

**Time tip:** Steps 1–3 set up the skill. Step 4 tests it in Cursor chat (uses one Agent request).

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

- `name` identifies the skill in Cursor's skill list.
- `description` tells Cursor when to suggest this skill — it matches against what you type in chat.

Put environment requirements you would like to check in the **markdown body**.

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
---

## What This Skill Does

Analyzes GitHub repository health by running two data tools and synthesizing
results with causal reasoning. The tools return structured data with indicator
flags — the agent provides interpretation and judgment.

## Prerequisites

Before running the scripts, confirm:
- Python 3.11+ and `uv` are available
- `.env` has `GITHUB_TOKEN` (and `GROQ_API_KEY` if you call Groq)

If a command fails because a token or tool is missing, stop and tell the user
what to install or set. Do not guess metrics.

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
- **Every causal claim acknowledges an alternative explanation.** For any detected
  pathway or observed symptom, evaluate both the hypothesized mechanism and plausible
  competing explanations (e.g. intentional API stability, seasonal variation, or scope
  shifts) before drawing conclusions. Do not cite alternative explanations for pathways
  that were not detected.
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

The `description` field is how Cursor decides when to activate your skill — write it carefully. The description is injected into the Cursor system prompt. You can edit the wording later; this version matches the tools you built in **Build**. You can also invoke the skill yourself: in chat, type `/` and choose **repo-health-analyst** (or type `/repo-health-analyst`).

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

#### 4. Test in Cursor (uses one Agent request)

Open chat (**Cmd+L** / **Ctrl+L**) and ask:

> Analyze the health of pallets/flask

This is how you confirm the skill works *inside* Cursor — chat activates it. Cursor **may** load your skill, run your scripts, and follow your rules. If it does not, confirm the skill path and `description` in `SKILL.md`.

**No chat quota left?** **Deploy** is still complete once `SKILL.md` and `scripts/tools.py` are in place — you packaged the skill even if you could not demo it in chat.

### What you packaged


| Layer      | Artifact                                     |
| ---------- | -------------------------------------------- |
| Capability | `scripts/tools.py`                           |
| Rules      | `SKILL.md`                                   |
| Runtime    | Cursor (or any Agent Skills-compatible tool) |


You now have **two deployments** of the same logic:

1. `src/agent.py` — standalone Groq agent
2. `.cursor/skills/...` — editor-integrated skill

### ADLC deploy note

Version your skill (`metadata.version` in frontmatter) — the same discipline as version pinning and rollback in production. Full deployment also integrates agents into business workflows (APIs, CRM, ticketing), defines fallbacks when tools fail, and monitors latency and task-completion rates after launch.

---

## Evaluate: Causal vs naive agent (7 min)

plan → build → test → deploy → **evaluate** → operate → monitor

Behavioral comparison made visible, then map what you built to production. *(Evaluate is a workshop label — not an IBM ADLC phase name.)*

This is the payoff for **Test**. You built two agents on the same query; now compare them side by side and close with how the same architecture scales beyond the workshop.

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
uv run python docs/canvas/install.py
```

That copies `docs/canvas/agent-comparison.canvas.tsx` into Cursor's managed canvases folder for this workspace. The script prints the destination path when it succeeds.

*Or copy manually if you prefer not to run the script:*

- **macOS / Linux:**
  ```bash
  PROJECT_SLUG=$(echo "$PWD" | sed 's|^/||; s|/|-|g')
  mkdir -p "$HOME/.cursor/projects/$PROJECT_SLUG/canvases"
  cp docs/canvas/agent-comparison.canvas.tsx "$HOME/.cursor/projects/$PROJECT_SLUG/canvases/"
  ```
- **Windows (PowerShell):**
  ```powershell
  $slug = ($PWD.Path -replace '^/','' -replace '^[A-Za-z]:','' -replace '[\\/]','-').Trim('-')
  $dest = "$env:USERPROFILE\.cursor\projects\$slug\canvases"
  New-Item -ItemType Directory -Force -Path $dest
  Copy-Item docs\canvas\agent-comparison.canvas.tsx $dest\
  ```

> **Why ~/.cursor?** Canvases must live in Cursor's managed project sandbox (`~/.cursor/projects/<slug>/canvases/`) to compile and render live components. Because this directory lives outside your workspace root, it won't appear in the sidebar file explorer.

**To view the canvas in Cursor:**

1. Press **`Cmd + Shift + P`** (macOS) or **`Ctrl + Shift + P`** (Windows) to open the Command Palette.
2. Type **`View: Open Canvas`** (or simply **`Open Canvas`**) and press **Enter**.
3. Cursor opens the dedicated Canvas viewer. In the canvas list, select **`agent-comparison`** to display the live interactive comparison panel beside your terminal!

*(Note: Opening `.canvas.tsx` directly in the editor opens the raw TypeScript source code because VS Code defaults to the code editor for `.tsx` files. The live React renderer is accessed via the `View: Open Canvas` view.)*

The canvas shows:


|               | Causal agent            | Naive agent                                    |
| ------------- | ----------------------- | ---------------------------------------------- |
| Data source   | GitHub API (tool calls) | No tools — often guesses or pretraining recall |
| Context       | z-scores, benchmarks    | Raw numbers or guesses                         |
| Causal claims | Tier + alternatives     | Unqualified assertions                         |


Plus abbreviated sample narratives so you know what *grounded* vs *ungrounded* output looks like.

### Step 3 — Discuss (2 min)

With your terminal output and the canvas open, answer as a group:

1. Did the naive agent quote any number the causal agent did not retrieve?
2. Did the causal agent state an evidence tier and an alternative?
3. Which briefing would you send to a colleague deciding whether to adopt the repo?

### Step 4 — From workshop to production (2 min)

What you built today maps to a production stack — same layers, different packaging:


| Layer                            | What you built                     | Production equivalent                                         |
| -------------------------------- | ---------------------------------- | ------------------------------------------------------------- |
| Data intelligence                | `tools.py`                         | Shared library or service — facts, flags, evidence tiers only |
| Live data / tools                | `agent.py` `TOOLS` + dispatch      | MCP server, API gateway, or host-native function calling      |
| Knowledge retrieval *(optional)* | — *(not in this workshop)*         | RAG — vector search over docs, playbooks, policies            |
| Orchestration                    | Groq loop + `SYSTEM_PROMPT`        | Agent runtime — routing, guardrails, memory, fallbacks        |
| Deploy                           | Agent Skill (`SKILL.md` + scripts) | Skills + MCP + workflow hooks (Slack, CRM, ticketing)         |
| Operate / monitor *(optional)*   | Commented Langfuse in `agent.py`   | [Langfuse](https://langfuse.com) — traces, spans, tool calls, latency, token cost |


**Agent runtime** — the orchestration row above. In **Test**, that is your `run_agent` loop: it calls the Groq API each turn, reads tool-call requests from the model, runs your Python functions, and appends results back into the conversation until the model returns a final answer. In production, the runtime is the same idea at larger scale — often a service or framework (LangGraph, custom Python, Cursor's agent host) that:

- **Invokes the LLM API** — sends messages, receives completions (inference happens on the provider's side; the runtime is the client)
- **Executes the tool loop** — parse tool calls, dispatch to MCP or local functions, feed results back
- **Applies guardrails** — system prompt, routing rules, max turns, policy checks
- **Handles failures** — retries, alternate model, graceful errors when Groq or GitHub is down

The runtime is the **conductor**, not the musician: it does not host model weights, and it is not your data layer (`tools.py`) or tool server (MCP). Token cost and latency are tracked here because this is where inference calls originate.

**Langfuse** — fits the **operate / monitor** row. In **Test**, the commented `@observe` decorators on `groq_chat`, `run_agent`, and `run_naive_agent` are the workshop hook: uncomment them after setting `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, and `LANGFUSE_HOST` in `.env` to record each Groq turn, nested tool calls, and latency. In production, Langfuse (or similar) answers: *Which tool failed? Which prompt version drifted? What did each run cost?*

**MCP (Model Context Protocol)** — standardizes how AI hosts (Cursor, Claude Desktop, internal platforms) discover and call external tools. It fits the **live data / tools** row: one server exposing `get_repo_health` and `analyze_causal_patterns` so every host shares the same governed API, auth, and audit trail. MCP does **not** replace what you learned today:

- The **data-intelligence boundary** still lives in your Python return shapes (no opinions in tools, evidence tiers in causal output).
- **Orchestration** still needs an agent loop, system prompt, and routing rules ("call health first, then causal if flags fire").
- **Skills** and MCP are complementary — a Skill carries *how to interpret* results; MCP carries *how to invoke* the tools.

**RAG vs Skills** — both can add context to the prompt, but they solve different problems. **Skills** (**Deploy**) package curated **capability + rules** — when to activate, which scripts to run, how to interpret output. **RAG** searches a **large or fast-changing doc corpus** per query (policies, wikis, past reports). Use RAG when that knowledge is too big or dynamic to maintain in `SKILL.md`; use Skills when you need a versioned workflow with executable tools. RAG **complements** live API tools — it does not replace `tools.py` or evidence tiers; retrieved text can still be associative.

**Evaluation harness** — a set of repeatable checks teams use to judge whether an agent still produces trustworthy, grounded output after changes to the prompt, model, skill, or tools. The idea is similar to regression tests for code, but the behavior is probabilistic — so cases and assertions often focus on tool use and grounding rather than an exact string match. In this workshop, Step 3 is a lightweight manual version of that pattern; in production, teams often automate it as a scripted suite they can rerun in CI.

- **Cases** — a prompt, repo, and expected tool calls (here: causal vs naive on the same query)
- **Assertions** — checks on the final answer, such as citing tool output and stating tier + alternative (here: the three Step 3 questions)
- **Golden tool tests** — known repos with expected flags (here: **Build** checkpoints)
- **When to rerun** — commonly after prompt, model, or skill changes
- **What to test where** — deterministic flag and metric logic often belongs in `tools.py`; behavioral checks (e.g. skipped tools or ungrounded numbers) may need the full agent loop

**Other production essentials** (beyond what fits in 75 minutes):

- **Monitoring** — latency, task completion, tool-call failures, token cost (the commented Langfuse lines in `agent.py` are the workshop hook for this)
- **Access control** — least-privilege tokens; deployed agents get their own identity and inherited permissions
- **Fallbacks** — what happens when GitHub rate-limits, Groq is down, or the model skips a tool call
- **Versioning** — pin model, prompt, and skill versions; rollback when behavior drifts

---

## Optional: Operate & monitor discussion (8 min)

*Skip this section in a 75-minute session unless you have extra time. The [Evaluate section](#evaluate-causal-vs-naive-agent-7-min) is the recommended wrap-up.*

plan → build → test → deploy → **operate** → **monitor**

What happens after deploy once the agent is live.

ADLC does not end at deploy. Operate-and-monitor practices track latency, task completion, tool failures, and model drift, plus audits for permissions and compliance. Production agents also need visible reasoning (sources, not just answers), clear accountability (data owners maintain guidance; users own decisions), and access control that inherits existing permissions.

### Discussion questions (optional)

1. **The boundary test.** `is_declining` uses z-score < -1.0. Is the threshold a fact or a judgment? Where does the line fall?
2. **Evidence tiers.** What data would you need to move from Tier 2 (pattern) to Tier 3 (peer comparison)?
3. **Prompt sensitivity.** Remove one rule from `SYSTEM_PROMPT` and re-run. How much intelligence came from tools vs. instructions?
4. **Same data, different users.** How would you change the prompt (not the tools) for a CTO vs. a new contributor?

### What you would add for production (operate & monitor)

See [Step 4 — From workshop to production](#step-4--from-workshop-to-production-2-min) for the production architecture overview (layers, MCP, RAG, monitoring, access control). This optional section goes deeper on ongoing discipline:

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
│   ├── agent.py                       # ← you create in Test
│   ├── config.py                      # Groq model selection (GROQ_MODEL)
│   ├── list_models.py                 # Lists available Groq models
│   ├── tools.py                       # Build (you implement these)
│   └── verify.py                      # Setup verification
├── .cursor/skills/                    # ← you create in Deploy
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

# After completing Build — test health metrics
uv run --directory src python -c "from tools import get_repo_health; import json; print(json.dumps(get_repo_health('pallets','flask'), indent=2, default=str))"

# After completing Test — run the causal agent
uv run src/agent.py
uv run src/agent.py "Analyze the health of facebook/react"

# After completing Deploy — optional: run skill scripts from terminal
# uv run python .cursor/skills/repo-health-analyst/scripts/tools.py health pallets flask
# uv run python .cursor/skills/repo-health-analyst/scripts/tools.py causal pallets flask
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
