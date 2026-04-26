from transformers import pipeline

CACHE = {}
_pipe = None


# =========================
# LOAD MODEL ONCE
# =========================
def get_pipeline():
    global _pipe

    if _pipe is None:
        print("🤖 Loading FLAN-T5 model...")

        _pipe = pipeline(
            "text-generation",
            model="google/flan-t5-base",
            tokenizer="google/flan-t5-base"
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
This vulnerability can be exploited by attackers to compromise system security or sensitive data.

3. Attack scenario:
Attackers target {rule_id} to gain unauthorized access, execute malicious code, or leak data.

4. Fix:
Developers should avoid insecure coding practices, validate inputs, and use secure alternatives.
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

        # 🔥 IMPROVED PROMPT (STRONG + PRACTICAL)
        prompt = f"""
You are a cybersecurity expert teaching students.

Explain the vulnerability in a practical and real-world way.

Vulnerability: {rule_id}
Description: {message}

Format your answer:

1. Simple Explanation (what it is)
2. Why attackers care about it
3. Real-world attack scenario
4. Proper fix for developers

Rules:
- Do NOT repeat only the vulnerability name
- Be clear and practical
- Use simple English for students
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