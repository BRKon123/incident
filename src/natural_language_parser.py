from file_parser import FileParser


class NaturalLanguageParser(FileParser):
    def __init__(self, filepath: str, pydantic_model):
        # Lazy load imports so requirements.txt is fine
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from huggingface_hub import login
        import torch
        import os
        from dotenv import load_dotenv
        # Initialize LLM components
        load_dotenv()
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found in environment variables")
        
        login(token=hf_token)
        
        # Initialize model and tokenizer as instance variables
        self.model_name = "meta-llama/Llama-3.2-1B"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.llm = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        
        # Call parent constructor after initializing LLM components
        super().__init__(filepath, pydantic_model)

    def _generate_prompt(self, text: str) -> str:
        return f"""
Generate json document that reflects what the user states below.
The format of the json document must either follow schema1:
{{
  "users": ["alice", "bob", "charlie"],
  "handover_start_at": "2023-11-17T17:00:00Z",
  "handover_interval_days": 7
}}
Or schema2:
{{
  "overrides": [
    {{
      "user": "charlie",
      "start_at": "2023-11-20T17:00:00Z",
      "end_at": "2023-11-20T22:00:00Z"
    }}
  ]
}}
The format depends on the user query, and which model is more appropriate.
You must strictly follow one of the two schemas above, if neither is possible
then say that this generation is not possible
The user query:
{text}
Your response must be a json document:
"""

    def _extract_json(self, text: str) -> dict:
        # More lazy loads for requirements.txt to be valid
        import re
        import json
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in generated response")
        
        json_str = json_match.group()
        return json.loads(json_str)

    def _read_file(self) -> dict:
        # Read the natural language text from file
        with open(self.filepath, 'r') as f:
            text = f.read().strip()

        # Generate prompt and get model inputs
        prompt = self._generate_prompt(text)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to("mps") for k, v in inputs.items()}
        # Generate response using self.llm instead of self.model
        output = self.llm.generate(**inputs, max_length=500, do_sample=True, top_p=0.95, top_k=50)
        generated_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        response = generated_text.split(prompt)[1]
        print("\n\n\nthe response: ")
        print(response)
        # Extract and return JSON
        extracted_json = self._extract_json(response)
        print("extracted json everyone: ")
        print(extracted_json)
        return extracted_json