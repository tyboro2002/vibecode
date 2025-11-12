import re
import time
from datetime import datetime

from fastapi import FastAPI
import torch
from transformers import pipeline
from pydantic import BaseModel

pipe = None

app = FastAPI()

@app.on_event("startup")
def startup_event():
    global pipe
    print(f"Starting up... {datetime.now().isoformat()}")
    start = time.time()
    pipe = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        dtype=torch.bfloat16,
        device_map="auto",
    )
    end = time.time()

    print(f"Pipeline ready, took {(end - start)} seconds")

class CodeRequest(BaseModel):
    code: str = ""
    prompt: str = ""
@app.post("/")
def generate_response(request: CodeRequest):
    global pipe
    messages = [
        {
            "role": "system",
            "content": "answer in python markdown",
        },
        {"role": "user", "content": request.prompt + "\n the current code is: " + request.code + "\n anwer in python markdown"},
    ]
    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    code = outputs[0].get("generated_text", "")
    matches = re.findall(r"```python\n(.*?)\n```", code, flags=re.S)
    matches3 = re.findall(r"```\n(.*?)\n```", code, flags=re.S)

    code = "\n\n".join(matches) if matches else ("\n\n".join(matches3) if matches3 else code)

    return {"code": code}