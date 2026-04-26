from transformers import pipeline

CACHE = {}
_pipe = None


# =========================
# LOAD MODEL (ONCE)
# =========================
def get_pipeline():
    global _pipe

    if _pipe is None:
        print("🤖 Loading FLAN-T5 model...")

        _pipe = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )

        print("✅ Model loaded successfully")

    return _pipe


# =========================
# AI FUNCTION
# =========================
def call_ai(prompt):
    try:
        pipe = get_pipeline()

        result = pipe(
            prompt,
            max_new_tokens=220,
            do_sample=False
        )

        return result[0]["generated_text"]

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

2. Why dangerous:
This vulnerability may allow attackers to exploit weak coding practices and compromise system security.

3. Attack scenario:
Attackers target {rule_id} to gain unauthorized access, leak sensitive data, or execute malicious actions.

4. Fix:
Developers should follow secure coding practices, validate inputs, avoid unsafe functions, and store secrets securely.
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
        ai_output = CACHE[cache_key]

    else:

        # 🔥 STRONG PROMPT (IMPROVED)
        prompt = f"""
You are a senior cybersecurity engineer and teacher.

Explain this vulnerability in a simple and practical way for students.

Vulnerability: {rule_id}
Scanner Message: {message}

You must explain:

1. Simple Explanation (real meaning in simple terms)
2. Why attackers target this
3. Real-world attack scenario
4. Proper secure fix (developer mindset)

Rules:
- Do NOT repeat only the vulnerability name
- Avoid generic answers
- Be practical and educational
- Use simple English
"""

        ai_output = call_ai(prompt)

        if not ai_output:
            print("⚠ Using fallback explanation")
            ai_output = fallback(rule_id, message)

        CACHE[cache_key] = ai_output

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Detected Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""