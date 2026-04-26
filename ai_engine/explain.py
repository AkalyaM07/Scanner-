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

# cache to avoid repeated API calls
CACHE = {}


# =========================
# AI CALL FUNCTION
# =========================

def call_ai(prompt):
    """
    Calls Hugging Face API safely
    """

    try:
        response = requests.post(
            API_URL,
            headers=HEADERS,
            json={"inputs": prompt},
            timeout=60
        )

        # Model loading case
        if response.status_code == 503:
            time.sleep(3)
            return call_ai(prompt)

        # API failure → return None (handled later)
        if response.status_code != 200:
            return None

        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0].get("generated_text", "")

        if isinstance(data, dict):
            return data.get("generated_text", "")

        return None

    except Exception:
        return None


# =========================
# FALLBACK EXPLANATION
# =========================

def fallback(rule_id, message):
    return f"""
Explanation: {message}

Why dangerous: This vulnerability can be exploited by attackers to compromise system security.

Hacker perspective: An attacker may use {rule_id} to gain unauthorized access or execute malicious actions.

Fix: Avoid insecure coding patterns and validate inputs properly.
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

        prompt = f"""
You are a cybersecurity expert helping beginner developers.

Explain this vulnerability in simple student-friendly language.

Vulnerability: {rule_id}
Details: {message}

IMPORTANT:
- Do NOT repeat only the vulnerability name
- First explain what the vulnerability actually means
- Then explain why it is dangerous
- Then explain how a hacker may exploit it
- Then explain how to fix it

Return ONLY in this format:

Explanation:
(Explain what this vulnerability means in 2 to 3 lines)

Why dangerous:
(Explain why it is risky)

Hacker perspective:
(Explain how attackers may use this)

Fix:
(Explain secure fix)
"""

        # =========================
        # AI OR FALLBACK DECISION
        # =========================

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

⚠️ Detected Message:
{message}

🤖 AI Analysis:
{ai_output}

==============================
"""