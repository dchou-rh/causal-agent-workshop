import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq

from tools import analyze_causal_patterns, get_repo_health

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

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

TOOL_FUNCTIONS = {
    "get_repo_health": get_repo_health,
    "analyze_causal_patterns": analyze_causal_patterns,
}

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


def run_agent(user_message: str) -> str:
    """Run the full agent loop: user -> LLM -> tools -> LLM -> response."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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


def run_naive_agent(user_message: str) -> str:
    """A naive agent with no tools and no reasoning rules — for comparison."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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
