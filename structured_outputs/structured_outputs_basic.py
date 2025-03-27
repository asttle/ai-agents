import os

import azure.identity
import openai
import rich
from dotenv import load_dotenv
from pydantic import BaseModel
import json

# Setup the OpenAI client to use either Azure, OpenAI.com, or Ollama API
load_dotenv(override=True)

try:
    with open('../config.json', 'r') as config_file:
        config = json.load(config_file)
        gh_token = config.get("GH_TOKEN", "")
        if not gh_token:
            print("GH_TOKEN not found in config.json or is empty")
            exit(1)
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)

if gh_token:
    client = openai.OpenAI(base_url="https://models.inference.ai.azure.com", api_key=gh_token)
    MODEL_NAME = os.getenv("GITHUB_MODEL", "gpt-4o")


class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


completion = client.beta.chat.completions.parse(
    model=MODEL_NAME,
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
    ],
    response_format=CalendarEvent,
)


message = completion.choices[0].message
if message.refusal:
    rich.print(message.refusal)
else:
    event = message.parsed
    rich.print(event)