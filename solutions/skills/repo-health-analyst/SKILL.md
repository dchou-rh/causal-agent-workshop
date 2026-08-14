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
