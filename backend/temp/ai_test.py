# Install transformers from source - only needed for versions <= v4.34
# pip install git+https://github.com/huggingface/transformers.git
# pip install accelerate
import sys

import torch
from transformers import pipeline
import re
import os


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")

def instructions():
    print("Create a sorting algorithm with the following requirements:")
    print()
    print("1: It should sort a list of integers in ascending order.")
    print("2: If a 3 is present in the list, it should be moved to the front of the list.")
    print("3: If a 7 is present in the list, it should be moved to the end of the list.")
    print("4: if a 69 is present in the list, the list should be in descending order instead.")
    print("5: the function has to be called custom_sort(l)")

    print()

    print("Type 'exit' to quit.")
    print("Type 'test' to run the current code.")

    print()

if __name__ == "__main__":
    pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16,
                    device_map="auto")
    code = ""

    clear_terminal()
    instructions()

    while True:
        prompt = input("You> ")
        print("\n")
        if prompt == "exit":
            break

        if prompt == "test":
            test_code = ""
            try:
                input_lists = """test_lists = [
    [5, 3, 8, 1, 7],
    [10, 2, 69, 4, 3],
    [7, 6, 5, 4, 3],
]"""
                test = """correct_lists = [
    [3, 1, 5, 8, 7],
    [69, 10, 4, 3, 2],
    [3, 4, 5, 6, 7]
]

for src, target in zip(test_lists, correct_lists):
    i = 1
    src_copy = src.copy()
    ret = custom_sort(src_copy)
    out = src_copy if ret is None else ret
    if out == target:
        print(f"PASS TEST {i}")
    else:
        print(f"FAIL TEST {i}: got {out}, expected {target}")
    i += 1"""

                test_code = input_lists + "\n" + code + "\n" + test

                exec(test_code)
            except Exception as e:
                print(f"Error during testing: {e}")

            continue

        messages = [
            {
                "role": "system",
                "content": "ANSWER ONLY IN PYTHON COMPATIBLE CODE",
            },
            {"role": "user", "content": prompt + "\n the current code is: " + code + "\n ANSWER ONLY IN CODE"},
        ]
        prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

        code = outputs[0]["generated_text"]

        clear_terminal()
        instructions()

        matches = re.findall(r"```python\n(.*?)\n```", code, flags=re.S)
        matches3 = re.findall(r"```\n(.*?)\n```", code, flags=re.S)

        ai_response = ""
        m = re.search(r"<\|assistant\|>\n(.*?)(?=```)", code, flags=re.S)
        if m:
            ai_response = m.group(1).strip()

	code = "\n\n".join(matches) if matches else ("\n\n".join(matches3) if matches3 else code)


        print(f"AI> {ai_response}")
        print(
            "----- Generated Code -----\n"
            + code
            + "\n--------------------------\n\n"
        )
