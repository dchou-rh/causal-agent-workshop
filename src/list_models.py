import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


client = Groq(api_key=os.environ["GROQ_API_KEY"])
response = client.models.list()
for model in response.data:
    print(model.id)