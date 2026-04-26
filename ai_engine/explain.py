from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

CACHE = {}
_pipe = None


# =========================
# SAFE MODEL LOADER
# =========================
def get_pipeline():
    global _pipe

    if _pipe is None:
        print("🤖 Loading FLAN-T5 model safely...")

        model_name = "google/flan-t5-base"

        # ✔ Direct model loading (avoids CI pipeline issues)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        _pipe = pipeline(
            task="text2text-generation",
            model=model,
            tokenizer=tokenizer
        )

        print("✅ Model loaded successfully")

    return _pipe


# =========================
# AI CALL FUNCTION
# =========================
def call_ai(prompt):
    try:
        pipe = get_pipeline()

        result = pipe(
            prompt,
            max_new_tokens=200,
            do_sample=False
        )

        # FLAN-T5 output handling
        if result and len(result) > 0:
            return result[0].get("generated_text", "")

        return None

    except Exception as e:
        print("⚠ AI Error:", e)
        return None


# =========================
# FALLBACK (SAFE OUTPUT)
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

    # ✔ cache optimization
    if cache_key in CACHE:
        return CACHE[cache_key]

    # =========================
    # STRONG PROMPT
    # =========================
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

    CACHE[cache_key] = ai_output

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