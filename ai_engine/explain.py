import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# =========================
# MODEL CONFIG
# =========================
MODEL_NAME = "google/flan-t5-base"

generator = None
tokenizer = None
model = None


# =========================
# LOAD MODEL ONCE
# =========================
def load_model():
    global generator, tokenizer, model

    if generator is None:
        print("🤖 Loading FLAN-T5 model...")

        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

        generator = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer
        )

        print("✅ Model loaded successfully")


# =========================
# AI CALL FUNCTION
# =========================
def call_ai(prompt):
    try:
        load_model()

        result = generator(
            prompt,
            max_new_tokens=220,
            do_sample=False
        )

        return result[0]["generated_text"]

    except Exception as e:
        print(f"⚠ AI Error: {e}")
        return None


# =========================
# FALLBACK (ONLY IF AI FAILS)
# =========================
def fallback(rule_id, message):
    return f"""
1. What is {rule_id}?
{message}. This means unsafe code is detected in the project.

2. Why is it dangerous?
Attackers may exploit this vulnerability to harm the system.

3. How can a hacker misuse it?
They can use it to gain unauthorized access or steal data.

4. How to fix it?
Remove unsafe patterns and use secure coding practices.
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
A security vulnerability called "{rule_id}" was found in code.

Explain in very simple English:

1. What is {rule_id}?
2. Why is it dangerous?
3. How can a hacker misuse it?
4. How to fix it?

Keep explanation simple for students.
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