"""Lists every model your Groq API key currently has access to.
Run this if sql_generator.py's model name ever stops working — Groq
changes its free-tier lineup fairly often, so this checks the ground
truth instead of guessing a model name.
"""
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

for model in client.models.list().data:
    print(model.id)
