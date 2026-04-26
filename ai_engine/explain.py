from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

CACHE = {}
_model = None
_tokenizer = None


# =========================
# MODEL LOADER
# =========================
def load_model():
    global _model, _tokenizer

    if _model is None:
        print("🤖 Loading FLAN-T5 model...")
        model_name = "google/flan-t5-large"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("✅ Model loaded successfully")


# =========================
# AI CALL FUNCTION
# =========================
def call_ai(prompt):
    try:
        load_model()

        inputs = _tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )
        outputs = _model.generate(
            **inputs,
            max_new_tokens=200,
            num_beams=4,
            early_stopping=True
        )
        result = _tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result if result else None

    except Exception as e:
        print("⚠ AI Error:", e)
        return None


# =========================
# FALLBACK
# =========================
def fallback(rule_id, message):
    return f"""
1. What is {rule_id}?
{message}. This means sensitive information is exposed directly in the source code.

2. Why is it dangerous?
Anyone who reads the code can steal this information and misuse it.

3. How can a hacker misuse it?
A hacker can find this value in your code and use it to break into your system.

4. How to fix it?
Never write sensitive values directly in code. Use environment variables instead.
"""


# =========================
# MAIN FUNCTION
# =========================
def explain_issue(issue):
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    cache_key = f"{rule_id}_{path}_{line}"

    if cache_key in CACHE:
        return CACHE[cache_key]

    prompt = f"""You are a cybersecurity teacher explaining to beginner students.

A security vulnerability called "{rule_id}" was found in the code.

Answer these 4 questions in simple English:

1. What is {rule_id}? (explain in 2-3 simple lines what this vulnerability means)
2. Why is it dangerous? (explain the risk in 1-2 lines)
3. How can a hacker misuse it? (give a simple real example)
4. How to fix it? (give a simple solution in 1-2 lines)

Use very simple words. Assume the student has never heard of this vulnerability before."""

    ai_output = call_ai(prompt)

    if not ai_output:
        print("⚠ AI failed → using fallback")
        ai_output = fallback(rule_id, message)

    result = f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""

    CACHE[cache_key] = result
    return result