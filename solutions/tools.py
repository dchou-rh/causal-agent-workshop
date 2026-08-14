import os
import statistics
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from github import Github

load_dotenv()

gh = Github(os.environ["GITHUB_TOKEN"])


def get_repo_health(owner: str, repo: str) -> dict:
    """Retrieve health metrics with historical reference context.

    Returns structured data with indicator flags.
    Does NOT return opinions, recommendations, or severity labels.
    """
    r = gh.get_repo(f"{owner}/{repo}")
    now = datetime.now(timezone.utc)

    stats = r.get_stats_commit_activity()
    weekly_commits = [week.total for week in stats] if stats else []

    recent_4w = weekly_commits[-4:] if len(weekly_commits) >= 4 else weekly_commits
    recent_avg = statistics.mean(recent_4w) if recent_4w else 0

    hist_mean = statistics.mean(weekly_commits) if weekly_commits else 0
    hist_stdev = statistics.stdev(weekly_commits) if len(weekly_commits) >= 2 else 1.0
    z_score = (recent_avg - hist_mean) / hist_stdev if hist_stdev > 0 else 0.0

    contributors = list(r.get_stats_contributors() or [])
    if contributors:
        total_commits = sum(c.total for c in contributors)
        top_contributor_share = (
            max(c.total for c in contributors) / total_commits if total_commits else 0
        )
    else:
        total_commits = 0
        top_contributor_share = 0

    recent_issues = list(r.get_issues(state="all", since=now - timedelta(days=90)))
    open_issues = [i for i in recent_issues if i.state == "open" and i.pull_request is None]
    closed_issues = [i for i in recent_issues if i.state == "closed" and i.pull_request is None]

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
