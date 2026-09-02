"""Workshop data tools — implement these during Parts 1 and 2."""

import os
import statistics
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from github import Auth, Github

load_dotenv()

gh = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))


def get_repo_health(owner: str, repo: str) -> dict:
    """Retrieve health metrics with historical reference context.

    Returns structured data with indicator flags.
    Does NOT return opinions, recommendations, or severity labels.
    """
    raise NotImplementedError("Complete Part 1 of the workshop guide")


def _classify_trend(weekly: list[int]) -> str:
    """Classify commit trend from weekly counts."""
    raise NotImplementedError("Complete Part 1 of the workshop guide")


def analyze_causal_patterns(owner: str, repo: str) -> dict:
    """Scan repo events for matches against known causal pathways.

    Returns evidence for/against each pathway.
    Does NOT return which pathway "matters most" — that is the LLM's job.
    """
    raise NotImplementedError("Complete Part 2 of the workshop guide")


def _get_alternative(pathway_id: str) -> str:
    """Every causal claim must acknowledge at least one alternative."""
    raise NotImplementedError("Complete Part 2 of the workshop guide")
