import google.generativeai as genai
import os
import json


try:
    with open('../../config.json', 'r') as config_file:
        config = json.load(config_file)
        os.environ["GOOGLE_API_KEY"] = config.get("GOOGLE_GEMINI_KEY", "")
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)


# Configure the Gemini model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

PROMPT = """
Generate an ideal Dockerfile for {language} with best practices. Just share the dockerfile without any explanation between two lines to make copying dockerfile easy.
Include:
- Base image
- Installing dependencies
- Setting working directory
- Adding source code
- Running the application
- Exposing the port
- Healthcheck
- Command to start the application
- Multi-stage build if applicable
- Environment variables if applicable
- Labels if applicable
- User if applicable
- Volume if applicable
- Entrypoint if applicable
"""

def generate_dockerfile(language):
    response = model.generate_content(PROMPT.format(language=language))
    return response.text

if __name__ == '__main__':
    language = input("Enter the programming language: ")
    dockerfile = generate_dockerfile(language)
    print("\nGenerated Dockerfile:\n")
    print(dockerfile)
