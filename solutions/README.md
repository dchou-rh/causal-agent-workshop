# Solutions

Reference implementations for instructors. Do not share this folder with participants during the workshop.

| File | Workshop part |
|------|---------------|
| `config.py` | Shared Groq model selection |
| `tools.py` | Parts 1 + 2 |
| `agent.py` | Part 3 |
| `verify.py` | Pre-workshop setup |
| `skills/repo-health-analyst/` | Part 4 |

```bash
cp solutions/tools.py solutions/agent.py solutions/config.py src/
uv run --directory src python agent.py
```
