from transformers import pipeline

CACHE = {}
_pipe = None


def get_pipeline():
    global _pipe

    if _pipe is None:
        print("🤖 Loading FLAN-T5 model...")

        # ✔ CORRECT way for FLAN-T5
        _pipe = pipeline(
            "text2text-generation",
            model="google/flan-t5-base"
        )

        print("✅ Model loaded successfully")

    return _pipe


def call_ai(prompt):
    try:
        pipe = get_pipeline()

        result = pipe(
            prompt,
            max_new_tokens=220,
            do_sample=False
        )

        # ✔ FLAN-T5 returns "generated_text"
        return result[0]["generated_text"]

    except Exception as e:
        print("⚠ AI Error:", e)
        return None


def fallback(rule_id, message):
    return f"""
1. Simple Explanation:
{message}

2. Why dangerous:
Attackers can exploit this vulnerability to compromise system security.

3. Attack scenario:
Attackers target {rule_id} for unauthorized access or data leakage.

4. Fix:
Use secure coding practices and validate inputs properly.
"""


def explain_issue(issue):
    rule_id = issue.get("check_id", "Unknown")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    key = f"{rule_id}_{path}_{line}"

    if key in CACHE:
        return CACHE[key]

    prompt = f"""
You are a cybersecurity expert.

Explain the vulnerability clearly for students.

Vulnerability: {rule_id}
Description: {message}

Format:
1. Simple Explanation
2. Why dangerous
3. Attack scenario
4. Fix

Do not repeat the question. Be practical.
"""

    ai_output = call_ai(prompt)

    if not ai_output:
        print("⚠ Using fallback")
        ai_output = fallback(rule_id, message)

    CACHE[key] = ai_output

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