import json
from gradio_client import Client

import requests
from huggingface_hub import configure_http_backend

def backend_factory() -> requests.Session:
    session = requests.Session()
    session.verify = False
    return session

configure_http_backend(backend_factory=backend_factory)

# Load configuration from config file
try:
    with open('../config.json', 'r') as config_file:
        config = json.load(config_file)
        hf_token = config.get("HF_TOKEN", "")
        if not hf_token:
            print("HF_TOKEN not found in config.json or is empty")
            exit(1)
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)


try:
    # Create client with proper authentication
    client = Client(
        "Asttle/First_agent_template",
        hf_token=hf_token,
        ssl_verify=False
    )
    
    # Format the messages correctly according to the API documentation
    # The API expects a list of message dictionaries with specific structure
    messages = [
        {
            "role": "user",
            "content": "What is the weather in London?",
            "metadata": None,
            "options": None
        }
    ]
    
    # Make the prediction with the correctly formatted messages
    result = client.predict(
        messages=messages,  # Pass the properly formatted messages
        api_name="/interact_with_agent"
    )
    
    print("Result received:")
    
    # Extract and print just the agent's response text for readability
    if result and isinstance(result, list) and len(result) > 0:
        for message in result:
            if message.get("role") == "assistant":
                print("\nAgent's response:")
                print(message.get("content"))
    
except Exception as e:
    print(f"Error: {str(e)}")
    
    # Additional debugging information
    if "401" in str(e) or "Unauthorized" in str(e):
        print("\nAuthentication Error:")
        print("1. Check that your HF_TOKEN is correct")
        print("2. Verify that you have access to this Space")
        print("3. Make sure the Space name is correct (case-sensitive)")
    
    if "Repository Not Found" in str(e):
        print("\nRepository Not Found Error:")
        print("1. Check that the Space name is correct: 'Asttle/First_agent_template'")
        print("2. Verify that the Space exists and is public or you have access to it")
        print("3. Check for typos in the Space name")