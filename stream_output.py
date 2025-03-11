import os
import json
from openai import OpenAI

try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        os.environ["GITHUB_TOKEN"] = config.get("GH_TOKEN", "")
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)

token = os.environ["GITHUB_TOKEN"]
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "Give me 5 good reasons why I should exercise every day.",
        }
    ],
    model=model_name,
    stream=True,
    stream_options={'include_usage': True}
)

usage = None
for update in response:
    if update.choices and update.choices[0].delta:
        print(update.choices[0].delta.content or "", end="")
    if update.usage:
        usage = update.usage

if usage:
    print("\n")
    for k, v in usage.dict().items():
        print(f"{k} = {v}")
