import os

from dotenv import load_dotenv
from groq import Groq

from config import ALLOWED_MODELS, DEFAULT_MODEL, get_groq_model

load_dotenv()

current = get_groq_model()

print("Workshop models (set GROQ_MODEL in .env):")
for model_id in sorted(ALLOWED_MODELS):
    tags = []
    if model_id == DEFAULT_MODEL:
        tags.append("default")
    if model_id == current:
        tags.append("current")
    suffix = f" ({', '.join(tags)})" if tags else ""
    print(f"  {model_id}{suffix}")

print("\nAll models on your Groq account:")
client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.models.list()
for model in response.data:
    print(model.id)
