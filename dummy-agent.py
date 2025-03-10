import os
import json
from huggingface_hub import InferenceClient


# Load configuration from config file
try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        os.environ["HF_TOKEN"] = config.get("HF_TOKEN", "")
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)

os.environ['CURL_CA_BUNDLE'] = ''

# Create client
client = InferenceClient("meta-llama/Llama-3.2-3B-Instruct")

# Test the connection
try:
    output = client.text_generation(
        "The capital of France is",
        max_new_tokens=100,
    )
    print("Success! Output:")
    print(output)
except Exception as e:
    print(f"Error: {e}")