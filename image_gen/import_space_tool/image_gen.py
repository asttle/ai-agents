import json
from smolagents import CodeAgent, HfApiModel, Tool


try:
    with open('../../config.json', 'r') as config_file:
        config = json.load(config_file)
        hf_token = config.get("HF_TOKEN", "")
        if not hf_token:
            print("HF_TOKEN not found in config.json or is empty")
            exit(1)
except FileNotFoundError:
    print("Config file not found. Please create a config.json file with your tokens.")
    exit(1)

image_generation_tool = Tool.from_space(
    "black-forest-labs/FLUX.1-schnell",
    name="image_generator",
    description="Generate an image from a prompt"
)

model = HfApiModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct", token=hf_token)

agent = CodeAgent(tools=[image_generation_tool], model=model)

agent.run(
    "Improve this prompt, then generate an image of it.", 
    additional_args={'user_prompt': 'iphone 18 design'}
)