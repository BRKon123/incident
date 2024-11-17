from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login
import torch, os
from dotenv import load_dotenv
import json
import re

load_dotenv()
print("my token lol: ",os.getenv("HF_TOKEN"))
login(token=os.getenv("HF_TOKEN"))

model_name = "meta-llama/Llama-3.2-1B"

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
)

# Prepare the input prompt
prompt = """
Generate json document that reflects what the user states below.
The format of the json document should either like this:
{
  "users": ["alice", "bob", "charlie"],
  "handover_start_at": "2023-11-17T17:00:00Z",
  "handover_interval_days": 7
}
Or like this:
{
  "overrides": [
    {
      "user": "charlie",
      "start_at": "2023-11-20T17:00:00Z",
      "end_at": "2023-11-20T22:00:00Z"
    }
  ]
}
The format depends on the user query, and which model is more appropriate.
The user query:
start time is 2024 november 30th at 5pm, handover interval days is 5, and users are john henry and adam
Your response must be a json docuemnt:
"""
inputs = tokenizer(prompt, return_tensors="pt")

# Move inputs to MPS device
inputs = {k: v.to("mps") for k, v in inputs.items()}

# Generate a response
output = model.generate(**inputs, max_length=500, do_sample=True, top_p=0.95, top_k=50)

# Decode and print the response
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
response = generated_text.split(prompt)
print(response)

# Extract JSON using regex
json_match = re.search(r'\{.*\}', response[1], re.DOTALL)
if json_match:
    json_str = json_match.group()
    # Parse the JSON string into a Python object
    json_obj = json.loads(json_str)
    print("\nParsed JSON:")
    print(json.dumps(json_obj, indent=2))
else:
    print("No JSON found in response")
