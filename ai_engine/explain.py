import os
import requests
import time

# =========================
# CONFIG
# =========================

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"
HF_TOKEN = os.getenv("HF_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
} if HF_TOKEN else {}

CACHE = {}

# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt, retries=3):
    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        # Model loading → retry
        if response.status_code == 503 and retries > 0:
            time.sleep(2)
            return call_ai(prompt, retries - 1)

        # Failure
        if response.status_code != 200:
            return None

        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "").strip()

        if isinstance(data, dict):
            return data.get("generated_text", "").strip()

        return None

    except Exception:
        return None


# =========================
# FALLBACK
# =========================

def fallback(rule_id, message):
    return f"""
Explanation:
{message}

Why Dangerous:
Attackers can exploit this vulnerability to compromise the system or gain unauthorized access.

Hacker Perspective:
Hackers look for {rule_id} issues to break into systems or execute malicious code.

Fix:
Use secure coding practices and avoid unsafe operations.
""".strip()


# =========================
# MAIN FUNCTION
# =========================

def explain_issue(issue):
    rule_id = issue.get("check_id", "UNKNOWN")
    path = issue.get("path", "Unknown file")
    line = issue.get("start", {}).get("line", "N/A")
    message = issue.get("extra", {}).get("message", "No details")

    cache_key = f"{rule_id}_{path}_{line}"

    # Cache check
    if cache_key in CACHE:
        ai_output = CACHE[cache_key]
    else:

        prompt = f"""
You are a cybersecurity expert.

Explain the following vulnerability in very simple terms.

Vulnerability: {rule_id}
Details: {message}

Give output in this format:

Explanation:
Why Dangerous:
Hacker Perspective:
Fix (with simple example if possible):
"""

        if HF_TOKEN:
            ai_output = call_ai(prompt)

            if not ai_output:
                ai_output = fallback(rule_id, message)
        else:
            ai_output = fallback(rule_id, message)

        CACHE[cache_key] = ai_output

    return f"""
==============================

🔴 Issue: {rule_id}
📄 File: {path} (Line {line})

⚠️ Message:
{message}

🤖 AI Explanation:
{ai_output}

==============================
"""