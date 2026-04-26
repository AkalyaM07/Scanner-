import time
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# =========================
# MODEL
# =========================
MODEL_NAME = "google/flan-t5-base"

tokenizer = None
model = None


# =========================
# LOAD MODEL ONCE
# =========================
def load_model():
    global tokenizer, model

    if model is None:
        print("🤖 Loading FLAN-T5 model...")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

        model.eval()

        print("✅ Model loaded successfully")


# =========================
# AI CALL (NO PIPELINE)
# =========================
def call_ai(prompt):
    try:
        load_model()

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=220,
                do_sample=False
            )

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    except Exception as e:
        print(f"⚠ AI Error: {e}")
        return None


# =========================
# FALLBACK (ONLY IF AI FAILS)
# =========================
def fallback(rule_id, message):
    return f"""
1. What is {rule_id}?
{message}. This means unsafe code is found in the project.

2. Why is it dangerous?
Attackers may exploit this vulnerability.

3. How can a hacker misuse it?
They can gain unauthorized access or steal data.

4. How to fix it?
Use secure coding practices and avoid unsafe functions.
"""


# =========================
# MAIN FUNCTION
# =========================
def explain_issue(issue):
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    prompt = f"""
A security vulnerability "{rule_id}" is found.

Explain simply:

1. What is it?
2. Why dangerous?
3. How can attacker misuse it?
4. How to fix it?

Use simple English for students.
"""

    ai_output = call_ai(prompt)

    if not ai_output:
        print("⚠ AI failed → using fallback")
        ai_output = fallback(rule_id, message)

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""