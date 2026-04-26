from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

CACHE = {}
_model = None
_tokenizer = None


# =========================
# SAFE MODEL LOADER
# =========================
def load_model():
    global _model, _tokenizer

    if _model is None:
        print("🤖 Loading FLAN-T5 model...")
        model_name = "google/flan-t5-base"
        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        print("✅ Model loaded successfully")


# =========================
# AI CALL FUNCTION
# =========================
def call_ai(prompt):
    try:
        load_model()

        inputs = _tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = _model.generate(**inputs, max_new_tokens=200)
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
1. Simple Explanation:
{message}

2. Why it is dangerous:
This vulnerability can allow attackers to exploit weak coding practices and compromise system security.

3. Attack scenario:
Attackers target {rule_id} to gain unauthorized access, steal data, or execute malicious code.

4. Fix:
Avoid insecure coding patterns, validate inputs, and use secure alternatives.
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

    prompt = f"""
You are a senior cybersecurity engineer teaching students.

Explain the vulnerability in simple and practical terms.

Vulnerability: {rule_id}
Description: {message}

Provide response in this format:

1. Simple Explanation
2. Why attackers target it
3. Real-world attack scenario
4. Secure fix for developers

Rules:
- Do NOT repeat only the name
- Be practical and beginner-friendly
- Use simple English
"""

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