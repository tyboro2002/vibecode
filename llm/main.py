import re
import time
from datetime import datetime

from fastapi import FastAPI
import torch
from transformers import pipeline
from pydantic import BaseModel

model_name = "meta-llama/Llama-3.2-1B-Instruct"
pipe = None
app = FastAPI()

@app.on_event("startup")
def startup_event():
    global pipe
    print(f"Starting up... {datetime.now().isoformat()}")
    start = time.time()
    pipe = pipeline(
        "text-generation",
        model=model_name,
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
        {"role": "user", "content": request.prompt + "\n the current code is: " + request.code},
    ]

    code = pipe(messages, max_new_tokens=256)[0]["generated_text"][-1]['content']

    matches = re.findall(r"```python\n(.*?)\n```", code, flags=re.S)
    matches3 = re.findall(r"```\n(.*?)\n```", code, flags=re.S)

    code = "\n\n".join(matches) if matches else ("\n\n".join(matches3) if matches3 else code)

    return {"code": code}
