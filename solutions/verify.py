import os

from dotenv import load_dotenv
from github import Github
from groq import Groq

from config import get_groq_model

load_dotenv()

# Test GitHub
gh = Github(os.environ["GITHUB_TOKEN"])
repo = gh.get_repo("pallets/flask")
print(f"GitHub OK: {repo.full_name} ({repo.stargazers_count} stars)")

# Test Groq
client = Groq(api_key=os.environ["GROQ_API_KEY"])
model = get_groq_model()
resp = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Say 'ready' and nothing else."}],
)
print(f"Groq model: {model}")
print(f"Groq OK: {resp.choices[0].message.content}")
