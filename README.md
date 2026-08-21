# Build an Intelligence Agent, Not a Chatbot

**A 90-minute workshop on causal reasoning with AI agents.**

> *Not what happened. Why it happened. What happens next.*

Most AI agent tutorials teach you to wire an LLM to an API and call it done. The result is a chatbot that retrieves data and parrots it back. This workshop teaches something deeper: how to build agents that **reason causally** about data — contextualizing metrics, distinguishing correlation from causation, and communicating confidence honestly.

**Domain:** Open-source project health (GitHub)  
**LLM:** Groq API — free, no credit card  
**Data:** GitHub REST API via PyGithub  
**Editor:** Cursor (free Hobby plan)  
**Language:** Python, managed with [uv](https://docs.astral.sh/uv/)

**Cost: $0.** Every tool in this workshop is free with no credit card required.

---



## Pre-Workshop Setup

Complete these steps **before the workshop.** We spend only ~5 minutes at the start verifying your setup.

### Prerequisites

- macOS or Windows
- Internet access
- A GitHub account
- About 20 minutes for first-time setup

No prior Python or terminal experience required — this guide installs everything you need and explains how to use the command line as you go.

---



### New to the terminal?

The **terminal** (also called the **command line** or **shell**) is a text-based way to talk to your computer. Instead of clicking buttons, you type commands and press **Enter**. This workshop uses it to install tools and run Python code.

**How to open a terminal**


| Platform    | Easiest option (use this for the workshop)        | Alternative                                                               |
| ----------- | ------------------------------------------------- | ------------------------------------------------------------------------- |
| **macOS**   | In Cursor: **View → Terminal**, or press `Cmd+``  | Open **Terminal** from Applications → Utilities                           |
| **Windows** | In Cursor: **View → Terminal**, or press `Ctrl+`` | Press the **Windows key**, type `PowerShell`, open **Windows PowerShell** |


A panel opens at the bottom of the screen with a blinking cursor. That is your terminal.

**How to run a command**

1. **Copy** the command from this guide (click the copy icon on the code block).
2. **Click inside the terminal** so it is focused.
3. **Paste** the command:
  - macOS: `Cmd+V`
  - Windows: `Ctrl+V` (or right-click → Paste in PowerShell)
4. Press **Enter**.
5. Wait for the command to finish. A new line with a cursor means it is ready for the next command.

**A few things to know**

- **Do not type the** `$` **or** `>` at the start of example lines — those just show where the prompt is.
- **One command at a time.** Run each code block separately unless the guide says otherwise.
- `cd` **means "go to this folder."** Example: `cd causal-agent-workshop` moves you into that project folder.
- **Errors are normal while learning.** Read the last few lines of output — they usually say what went wrong. See [Troubleshooting](#troubleshooting) at the bottom of this page.

> **Tip:** Complete Step 1 (install Cursor) first, then use **Cursor's integrated terminal** for every step below. You can keep the editor and terminal in one window.

---



### Step 1: Install Cursor

[Cursor](https://www.cursor.com) is a VS Code-based editor with AI features built in. The free Hobby plan is all you need.

1. Go to [cursor.com](https://www.cursor.com) and download the installer
2. Run the installer for your platform
3. Open Cursor and sign up (email or Google — no payment info needed)

> **What's included in the Hobby plan?** Per [Cursor's pricing page](https://cursor.com/pricing), Hobby is free forever with no credit card and includes:
>
> - The full VS Code-based editor (file explorer, integrated terminal, Git, extensions)
> - **Limited Agent requests** — enough for this workshop's Part 4 skill demo
> - **Access to Composer** — Cursor's multi-file editing mode
>
> Cursor does not publish exact monthly caps for the free tier. If you hit a limit during the workshop, the editor and terminal still work — you can finish all Python exercises from the command line with `uv run`. Check remaining usage in **Cursor Settings → Account**.

> VS Code works too. After Step 1, this guide uses Cursor's built-in terminal for everything — you do not need a separate terminal app.

---



### Step 2: Install Git

Open your terminal (see [New to the terminal?](#new-to-the-terminal) above).

**macOS (Homebrew):**

If you don't have [Homebrew](https://brew.sh) (a macOS package installer), install it first. Paste this command, press **Enter**, and follow the on-screen prompts (you may need to enter your Mac password — characters won't show as you type; that is normal):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

When Homebrew finishes, it may show extra commands to add it to your PATH. **Copy and run those too** if prompted.

Then install Git:

```bash
brew install git
```

**Windows (winget):**

Press the **Windows key**, type `PowerShell`, and open **Windows PowerShell**. Paste this command and press **Enter**:

```powershell
winget install --id Git.Git -e --source winget
```

If prompted, type `Y` and press **Enter** to confirm.

Close and reopen your terminal after installation (in Cursor: click the trash-can icon on the terminal panel, then open a new terminal with `Ctrl+`` or` Cmd+``).

**Verify (both platforms):**

```bash
git --version
```

You should see a version number (for example, `git version 2.47.0`). If you see `command not found`, close and reopen the terminal and try again.

---



### Step 3: Install uv and Python

[uv](https://docs.astral.sh/uv/) is a fast Python package manager. It also installs and manages Python for you — you do not need a separate Python installer.

In your terminal, run the command for your platform:

**macOS (Homebrew):**

```bash
brew install uv
```

**Windows (winget):**

```powershell
winget install --id astral-sh.uv -e --source winget
```

Close and reopen your terminal after installation.

**Verify uv (both platforms):**

```bash
uv --version
```

You should see something like `uv 0.7.x`.

**Install Python (both platforms):**

This workshop requires Python 3.11+. uv downloads it for you — paste and run:

```bash
uv python install 3.12
```

This may take a minute the first time while it downloads Python.

Verify:

```bash
uv python list
```

You should see `3.12` listed. You do not need to run `python` or `pip` directly — `uv run` handles the virtual environment for this project.

---



### Step 4: Clone This Repository

In Cursor, open the integrated terminal (**View → Terminal**, or `Ctrl+`` on Windows /` Cmd+`` on macOS).

**Clone** means "download a copy of the project from the internet." Run these commands one at a time:

```bash
git clone https://github.com/dchou-rh/causal-agent-workshop.git
cd causal-agent-workshop
```

Replace the URL above if your fork or organization uses a different path.

Finally, install the project's Python packages. If `uv` is not recognized, close and reopen Cursor so the terminal picks up the newly installed command.

```bash
uv sync
```

`uv sync` may take a minute the first time. When it finishes, you should be back at the prompt with no error messages.

`uv sync` creates a virtual environment, installs Python if needed, and installs all dependencies from `pyproject.toml`. You never need to run `pip install` or activate a venv manually — always use `uv run`.

---



### Step 5: Create the `.env` File

The workshop code reads API keys from a `.env` file in the project root. Create it now so you have somewhere to paste each key as you get it.

**Using the terminal** — make sure you are in the project root (the folder containing `src/`), then run:

```bash
cp .env.sample .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.sample .env
```

**Or using Cursor's file explorer (no terminal needed):**

1. In the left sidebar, find `.env.sample`
2. Right-click → **Copy**
3. Right-click in the folder → **Paste**
4. Rename the copy to `.env`

Now open `.env` by clicking it in the file explorer. You will see placeholder values — you will replace them in the next two steps.

The project loads `.env` automatically. **Never commit your** `.env` **file** — it is already in `.gitignore`.

---



### Step 6: Get a GitHub Personal Access Token (Free)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**
3. Name: `workshop`
4. Scopes: check only **public_repo**
5. Click **Generate token** and **copy it immediately**
6. Switch back to Cursor, open `.env`, and replace `ghp_your_token_here` with the token you just copied
7. Save the file (`Cmd+S` / `Ctrl+S`)

This gives you 5,000 API requests/hour. The workshop uses ~200.

---



### Step 7: Get a Groq API Key (Free, No Credit Card)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with email or Google — **no credit card required**
3. Go to **API Keys** at the top right
4. Click **Create API Key**, name it `workshop`, and copy it
5. Switch back to Cursor, open `.env`, and replace `gsk_your_key_here` with the key you just copied
6. Save the file (`Cmd+S` / `Ctrl+S`)

Groq gives you 14,400 requests/day on the free tier. The workshop uses about 30 to 200.

Your `.env` file should now look like this (with your real tokens):

```
GITHUB_TOKEN=ghp_abc123...
GROQ_API_KEY=gsk_xyz789...
```

> **Alternative (advanced):** If you prefer shell environment variables over a `.env` file, you can export them directly:
>
> ```bash
> # macOS / Linux
> export GITHUB_TOKEN="ghp_your_token_here"
> export GROQ_API_KEY="gsk_your_key_here"
> ```
>
> ```powershell
> # Windows PowerShell
> $env:GITHUB_TOKEN = "ghp_your_token_here"
> $env:GROQ_API_KEY = "gsk_your_key_here"
> ```
>
> These only last for the current session. To persist, add them to `~/.zshrc` (macOS/Linux) or use **System Settings → Environment Variables** (Windows).

---



### Step 8: Verify Everything Works

Make sure your terminal is in the project root (the folder containing `src/`), then run:

```bash
uv run src/verify.py
```

If you see `No such file or directory`, make sure you cloned the repo and are in the project root (the folder containing `src/`).

Expected output:

```
GitHub OK: pallets/flask (xxxxx stars)
Groq OK: ready
```

If either line fails:

- Open `.env` in Cursor and check that both tokens are present, with no extra spaces or quotes around the values
- Make sure the file is named exactly `.env` (not `.env.sample`, not `env.txt`)
- If you used shell exports instead of `.env`, verify they are set: `echo $GITHUB_TOKEN` (macOS/Linux) or `echo $env:GITHUB_TOKEN` (Windows PowerShell)
- If you get an error about a model not existing or not having access, run `uv run src/list_models.py` to see which models are available on your Groq account

---



## Workshop guide

The hands-on walkthrough is in **[docs/workshop-guide.md](docs/workshop-guide.md)**. It maps each section to **ADLC** (Agent Development Lifecycle) phases: Plan → Build → Test → Deploy → Govern.

### Quick reference


| Part   | File                                  | What you build                                   |
| ------ | ------------------------------------- | ------------------------------------------------ |
| Setup  | `src/verify.py`                       | Confirm GitHub + Groq access                     |
| Part 1 | `src/tools.py`                        | `get_repo_health` with contextual benchmarks     |
| Part 2 | `src/tools.py`                        | `analyze_causal_patterns` causal reasoning layer |
| Part 3 | `src/agent.py`                        | Full Groq agent with function calling            |
| Part 4 | `.cursor/skills/repo-health-analyst/` | Portable Agent Skill                             |




### Project structure

After setup, the repo looks like this. Files you create during the workshop are marked with **← you create**.

```
causal-agent-workshop/
├── .venv/                             # ← created by uv sync (virtual environment)
├── docs/
│   └── workshop-guide.md              # Hands-on workshop (ADLC-aligned)
├── solutions/                         # Instructor reference (optional)
│   ├── skills/
│   │   └── repo-health-analyst/
│   │       ├── scripts/
│   │       │   └── tools.py
│   │       └── SKILL.md
│   ├── README.md
│   ├── agent.py
│   ├── tools.py
│   └── verify.py
├── src/
│   ├── agent.py                       # ← you create in Part 3
│   ├── list_models.py                 # Lists available Groq models
│   ├── tools.py                       # Parts 1 + 2 (you implement these)
│   └── verify.py                      # Setup verification
├── .cursor/skills/                    # ← you create in Part 4
│   └── repo-health-analyst/
│       ├── scripts/
│       │   └── tools.py
│       └── SKILL.md
├── .env                               # ← you create in Step 5 (from .env.sample)
├── .env.sample                        # Template for API keys
├── .gitignore
├── .python-version
├── README.md                          # Setup instructions (this file)
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

---



## Troubleshooting

### Use Cursor to help you debug

If you run into an error, Cursor can help you figure it out:

1. **Highlight** the error text in the terminal or the problematic code in the editor
2. Press `Cmd+L` (macOS) or `Ctrl+L` (Windows) — this sends the highlighted text to Cursor's chat panel
3. Ask something like "What does this error mean?" or "How do I fix this?" or just hit enter.

Cursor can see your project files, so it often gives you a specific fix rather than a generic answer. This works for terminal errors, Python tracebacks, unexpected output — anything you can select.

### Common issues

**I don't know if I'm in the right folder**  
Run `pwd` (macOS) or `cd` (Windows) to see your current folder. The path should end in `causal-agent-workshop`. If it does not, run `cd causal-agent-workshop`. You can also run `ls` (macOS) or `dir` (Windows) to confirm you see `src/`, `docs/`, and `README.md` in the listing.

**Nothing happens when I paste a command**  
Click inside the terminal panel first so the cursor is blinking there, then paste and press **Enter**.

`command not found` **after installing something**  
Close the terminal and open a new one (trash-can icon → `Ctrl+`` or` Cmd+``), then try again.

`ModuleNotFoundError: No module named 'groq'`  
You ran `python` directly instead of `uv run`. Running `python src/verify.py` uses whatever Python is installed on your system, which does not have the workshop's packages. Running `uv run src/verify.py` uses the project's virtual environment (`.venv/`) where all the packages were installed by `uv sync`. Always use `uv run`.

`401 Bad credentials` **from GitHub**  
Your `GITHUB_TOKEN` is missing, expired, or incorrect. Re-check your `.env` file or shell exports.

`Invalid API Key` **from Groq**  
Your `GROQ_API_KEY` is missing or was copied incorrectly.

**GitHub API returns empty stats**  
Stats endpoints compute on first request and may return empty. Wait 5 seconds and try again.

**Groq returns** `rate_limit_exceeded`  
The free tier allows 30 requests/minute. Wait 60 seconds and retry.

`uv: command not found`  
Close and reopen your terminal after installing uv. On macOS, run `brew install uv` again. On Windows, run the winget command from Step 3 again.

`python: command not found`  
You do not need a system-wide `python` command. Run `uv python install 3.12`, then always use `uv run src/script.py` for workshop scripts.

---



## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Use it, adapt it, teach it.