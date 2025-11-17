import re
import time
from datetime import datetime

from fastapi import FastAPI
import torch
from transformers import pipeline
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-3B-Instruct"
model = None
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

app = FastAPI()

@app.on_event("startup")
def startup_event():
    global model
    print(f"Starting up... {datetime.now().isoformat()}")
    start = time.time()
    model = AutoModelForCausalLM.from_pretrained(
    	model_name,
    	torch_dtype="auto",
    	device_map="auto"
    )
    end = time.time()

    print(f"Pipeline ready, took {(end - start)} seconds")

class CodeRequest(BaseModel):
    code: str = ""
    prompt: str = ""
@app.post("/")
def generate_response(request: CodeRequest):
    global model
    global tokenizer
    messages = [
        {
            "role": "system",
            "content": "answer in python markdown",
        },
        {"role": "user", "content": request.prompt + "\n the current code is: " + request.code},
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    code = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


    matches = re.findall(r"```python\n(.*?)\n```", code, flags=re.S)
    matches3 = re.findall(r"```\n(.*?)\n```", code, flags=re.S)

    code = "\n\n".join(matches) if matches else ("\n\n".join(matches3) if matches3 else code)

    return {"code": code}
