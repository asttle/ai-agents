from transformers import AutoTokenizer, Gemma3ForConditionalGeneration
import json
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
# Load the instruction-tuned 4B model (for chat) – ensure your hardware is capable
model_name = "google/gemma-3-4b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name, token = hf_token)
model = Gemma3ForConditionalGeneration.from_pretrained(model_name, device_map="auto", token = hf_token)

prompt = "User: How does Gemma 3 compare to GPT-4?\nAssistant:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(response)